const express = require('express');
const fs = require('fs');
const fsp = require('fs/promises');
const path = require('path');
const { exec } = require('child_process');
const app = express();
const PORT = 3011;

app.use(express.static('.'));
app.use(express.json());

const RUN_FILE = 'run_number.txt';
let uiIteration = 0; // resets every time server starts

function getRunNumber() {
  try {
    return parseInt(fs.readFileSync(RUN_FILE, 'utf-8'), 10) || 0;
  } catch {
    return 0;
  }
}

function incrementRunNumber() {
  const current = getRunNumber() + 1;
  fs.writeFileSync(RUN_FILE, String(current));
  return current;
}

function formatTimestampForID(date = new Date()) {
  return date.toISOString().replace(/[:.]/g, '-').split('.')[0];
}

// Recursively copy directory
async function copyDir(src, dest) {
  await fsp.rm(dest, { recursive: true, force: true });
  await fsp.mkdir(dest, { recursive: true });
  const entries = await fsp.readdir(src, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      await copyDir(srcPath, destPath);
    } else {
      await fsp.copyFile(srcPath, destPath);
    }
  }
}

// Handle rankings + 3-version trajectory collection
app.post('/submit', (req, res) => {
  const { first, second, third, trajVersion = 'v1' } = req.body;
  const timestamp = new Date().toISOString();
  const runNumber = incrementRunNumber();
  const id = `UX_NNETNAV_TRAJ_WEBSITE_${runNumber}`;

  const line = `${timestamp},${id},${first},${second},${third}\n`;
  fs.appendFileSync('rankings.csv', line);
  console.log(` Ranking saved: ${line.trim()}`);
  res.send(' Preferences submitted!');


  const baseDir = '/Users/sniperjohn40/AutoUIUX_SAIL/NNetnav';
  const scriptPath = 'src/run_nnetnav.py';

  const seedMap = {
    '1': 'seed_states_webarena_persona_v1',
    '2': 'seed_states_webarena_persona_v2',
    '3': 'seed_states_webarena_persona_v3',
  };

  const websiteVersions = ['1', '2', '3'];

  const commands = websiteVersions.map(website => {
    const seedDir = `${baseDir}/${seedMap[website]}`;
    const resultDir = `UX_NNETNAV_TRAJ_WEBSITE_${runNumber}_TRAJ_${website}`;
    return `python3 ${scriptPath} \
      --model gpt-4o \
      --result_dir "${resultDir}" \
      --filter_dir DATA_NNETNAV \
      --seed_dir "${seedDir}" \
      --exploration_size_per_seed 1 \
      --n_jobs 4`;
  });

  const fullCommand = `cd "${baseDir}" && ` + commands.join(' && ');

  console.log(` Collecting trajectories (run #${runNumber})`);
  console.log(` Command:\n${fullCommand}`);

  exec(fullCommand, { cwd: baseDir }, (error, stdout, stderr) => {
    if (error) {
      console.error(` Trajectory collection error: ${error.message}`);
      return res.status(500).send(' Ranking saved, but trajectory collection failed.');
    }
    if (stderr) console.warn(`⚠️ stderr: ${stderr}`);
    console.log(` Trajectories collected (run #${runNumber})`);
    res.send(` Ranking saved and trajectories collected (run #${runNumber})`);
  });
});

// Handle one-version iteration + feedback
app.post('/run-iteration', async (req, res) => {
  const { version, userImprovements } = req.body;
  uiIteration += 1;

  const seedMap = {
    '1': 'seed_states_webarena_persona_v1',
    '2': 'seed_states_webarena_persona_v2',
    '3': 'seed_states_webarena_persona_v3',
  };

  const versionMap = {
    '1': 'version-1',
    '2': 'version-2',
    '3': 'version-3',
  };

  const seedSubdir = seedMap[version];
  const versionDir = versionMap[version];
  if (!seedSubdir || !versionDir) {
    return res.status(400).send(' Invalid version');
  }

  const baseDir = '/Users/sniperjohn40/AutoUIUX_SAIL/NNetnav';
  const seedDir = `${baseDir}/${seedSubdir}`;
  const testSiteSrc = `/Users/sniperjohn40/AutoUIUX_SAIL/Test_Site_2/${versionDir}`;
  const webContentDest = `/Users/sniperjohn40/AutoUIUX_SAIL/web_content`;
  const scriptPath = 'src/run_nnetnav.py';

  try {
    console.log(` Copying ${testSiteSrc} → ${webContentDest}`);
    await copyDir(testSiteSrc, webContentDest);
  } catch (err) {
    console.error(` Failed to copy files: ${err.message}`);
    return res.status(500).send(' Error copying version files');
  }

  const runNumber = incrementRunNumber();
  const resultDir = `UX_NNETNAV_TRAJ_WEBSITE_${runNumber}_TRAJ_${version}`;
  console.log(`📂 Using result_dir: ${resultDir} (run #${runNumber}, UI iteration ${uiIteration})`);

  if (userImprovements && userImprovements.trim()) {
    const feedbackFile = path.join(baseDir, `UX_Improvement_suggestions_${runNumber}_AJ.txt`);
    const feedbackText = `\n[Human Suggestion]:\n${userImprovements.trim()}\n`;
    fs.appendFileSync(feedbackFile, feedbackText, 'utf8');
    console.log(`✍️ Saved user suggestion to ${feedbackFile}`);
  }

  const command = `cd "${baseDir}" && python3 "${scriptPath}" \
    --model gpt-4o \
    --result_dir "${resultDir}" \
    --filter_dir DATA_NNETNAV \
    --seed_dir "${seedDir}" \
    --exploration_size_per_seed 1 \
    --n_jobs 4 \
    --use_personas \
    && python3 src/generate_ux_feedback_from_persona.py ${runNumber} \
    && python3 src/generate_ux_improvements_AJ.py ${runNumber} \
    && python3 src/code_improvement_AJ_4.py ${runNumber}`;

  console.log(` Running full command:\n${command}`);

  exec(command, { cwd: baseDir }, (error, stdout, stderr) => {
    if (error) {
      console.error(` Error: ${error.message}`);
      return res.status(500).send(' Error during script execution');
    }
    if (stderr) console.warn(`⚠️ stderr: ${stderr}`);
    console.log(` All scripts completed for Version ${version}`);
    res.send(` Iteration complete. Used result_dir: ${resultDir} (Iteration ${uiIteration})`);
  });
});

// Send UI-visible iteration count (resets every restart)
app.get('/iteration-count', (req, res) => {
  res.json({ iteration: uiIteration });
});

app.listen(PORT, () => {
  console.log(` Server running at http://localhost:${PORT}`);
  console.log(` UI iteration counter reset to 0`);
});
