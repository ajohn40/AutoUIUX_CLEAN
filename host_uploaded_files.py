from flask import Flask, send_from_directory, abort
from flask_cors import CORS
import os

CONTENT_FOLDER = 'web_content'
os.makedirs(CONTENT_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)

def get_single_site_folder():


    """
    If there's only one folder under `web_content/`, return it.
    If there are multiple, pick the latest modified one.
    If none, return None.
    """
    
    


    subdirs = [d for d in os.listdir(CONTENT_FOLDER)
               if os.path.isdir(os.path.join(CONTENT_FOLDER, d))]
    
    if not subdirs:
        return None

    if len(subdirs) == 1:
        return os.path.join(CONTENT_FOLDER, subdirs[0])

    # If more than one, return the most recently modified
    subdirs_full = [os.path.join(CONTENT_FOLDER, d) for d in subdirs]
    return max(subdirs_full, key=os.path.getmtime)

@app.route('/')
def index():
    site_folder = get_single_site_folder()
    if not site_folder:
        return "No uploaded site folder found in web_content/", 404

    index_file = os.path.join(site_folder, 'index.html')
    if os.path.exists(index_file):
        return send_from_directory(site_folder, 'index.html')
    return f"index.html not found in {os.path.basename(site_folder)}", 404

@app.route('/<path:path>')
def static_file(path):
    site_folder = get_single_site_folder()
    if not site_folder:
        return "No uploaded site folder found", 404

    full_path = os.path.join(site_folder, path)
    if os.path.exists(full_path):
        return send_from_directory(site_folder, path)
    return f"File not found: {path}", 404

if __name__ == '__main__':
    print(f"Hosting any subfolder found in: {CONTENT_FOLDER}")
    print("Access the hosted site at: http://localhost:8002/")
    app.run(host='0.0.0.0', port=8002, debug=True)

