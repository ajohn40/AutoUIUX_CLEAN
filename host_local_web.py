

from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import os

UPLOAD_FOLDER = 'web_content'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder=UPLOAD_FOLDER, static_url_path='')

CORS(app)

@app.route('/')
def index():
    try:
        return send_from_directory(UPLOAD_FOLDER, 'index.html')
    except FileNotFoundError:
        return jsonify({'message': 'Flask server is running', 'status': 'healthy'}), 200

@app.route('/<path:path>')
def static_file(path):
    return send_from_directory(UPLOAD_FOLDER, path)

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'files' not in request.files:
            return jsonify({'status': 'error', 'message': 'No files part in the request'}), 400

        files = request.files.getlist('files')
        
        if not files or all(file.filename == '' for file in files):
            return jsonify({'status': 'error', 'message': 'No files selected'}), 400

        uploaded_files = []
        for file in files:
            if file.filename:
                # Create subdirectories if the filename contains path separators
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                file.save(file_path)
                uploaded_files.append(file.filename)

        return jsonify({
            'status': 'success', 
            'message': f'{len(uploaded_files)} file(s) uploaded successfully',
            'files': uploaded_files
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Upload failed: {str(e)}'}), 500
    
    """
from flask_cors import CORS
CORS(app)

from flask import Flask, request, send_from_directory, jsonify
import os

UPLOAD_FOLDER = 'web_content/devportfolio'  # 🔄 Serve from inside devportfolio
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder=UPLOAD_FOLDER, static_url_path='')

@app.route('/')
def index():
    return send_from_directory(UPLOAD_FOLDER, 'index.html')

@app.route('/<path:path>')
def static_file(path):
    return send_from_directory(UPLOAD_FOLDER, path)

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files part in the request'}), 400

    files = request.files.getlist('files')
    for file in files:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))

    return jsonify({'status': 'success', 'message': f'{len(files)} file(s) uploaded'}), 200

if __name__ == '__main__':
    print(f"📂 Hosting from: {UPLOAD_FOLDER}")
    app.run(host='0.0.0.0', port=8003)


 """

from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import os

UPLOAD_FOLDER = 'web_content'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder=UPLOAD_FOLDER, static_url_path='')

# Initialize CORS after creating the app
CORS(app)

@app.route('/')
def index():
    try:
        return send_from_directory(UPLOAD_FOLDER, 'index.html')
    except FileNotFoundError:
        return jsonify({'message': 'Flask server is running', 'status': 'healthy'}), 200

@app.route('/<path:path>')
def static_file(path):
    return send_from_directory(UPLOAD_FOLDER, path)

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'files' not in request.files:
            return jsonify({'status': 'error', 'message': 'No files part in the request'}), 400

        files = request.files.getlist('files')
        
        if not files or all(file.filename == '' for file in files):
            return jsonify({'status': 'error', 'message': 'No files selected'}), 400

        uploaded_files = []
        for file in files:
            if file.filename:
                # Create subdirectories if the filename contains path separators
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                file.save(file_path)
                uploaded_files.append(file.filename)

        return jsonify({
            'status': 'success', 
            'message': f'{len(uploaded_files)} file(s) uploaded successfully',
            'files': uploaded_files
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Upload failed: {str(e)}'}), 500
    

@app.route('/generate-improvements', methods=['POST'])
def generate_improvements():
    data = request.get_json()
    
    user_request = data.get('user_request', '')
    files = data.get('files', [])

    suggestions = f"Improvements for request: \"{user_request}\""

    # 💾 Save suggestions to file
    save_path = '/Users/sniperjohn40/AutoUIUX_SAIL/NNetnav/UX_IMPROVEMENT_SUGGESTIONS_6_AJ.txt'
    try:
        with open(save_path, 'w') as f:
            f.write("USER REQUEST:\n")
            f.write(user_request + "\n\n")
            f.write("SUGGESTIONS:\n")
            f.write(suggestions + "\n")
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to write to suggestion file: {str(e)}'
        }), 500

    return jsonify({
        'status': 'success',
        'message': 'Improvements generated and saved to file',
        'suggestions': suggestions,
        'output_path': save_path
    }), 200



if __name__ == '__main__':
    print(f"Hosting from: {UPLOAD_FOLDER}")
    print("Server will be available at: http://localhost:8003")
    print("CORS enabled for cross-origin requests")
    app.run(host='0.0.0.0', port=8003, debug=True)

