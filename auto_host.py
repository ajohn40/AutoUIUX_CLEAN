import time
import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.server_process = None
        self.start_server()

    def start_server(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
        
        print("Starting server...")
        # Add environment variable to show Flask debug output
        env = os.environ.copy()
        env['FLASK_DEBUG'] = '1'
        self.server_process = subprocess.Popen(['python', 'host_uploaded_files.py'], env=env)

    def on_modified(self, event):
        if not event.is_directory:
            print(f" Detected change in: {event.src_path}")
            self.start_server()

    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            self.start_server()

def main():
    # Directory to watch
    watch_directory = 'web_content'
    
    
    # Ensure the directory exists
    os.makedirs(watch_directory, exist_ok=True)
    print(f"Created/verified directory: {watch_directory}")
    
    # List current files in directory
    print("\nCurrent files in directory:")
    for root, dirs, files in os.walk(watch_directory):
        for file in files:
            print(f"- {os.path.join(root, file)}")
    
    #Create event handler/observer
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, watch_directory, recursive=True)
    
    #observer
    observer.start()
    print(f"\nWatching directory: {watch_directory}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.server_process:
            event_handler.server_process.terminate()
    
    observer.join()

if __name__ == "__main__":
    main() 