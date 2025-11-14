import time
from pathlib import Path
from typing import Dict, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileOrganizerHandler(FileSystemEventHandler):
    def __init__(self, organizer):
        self.organizer = organizer
    
    def on_created(self,event):
        if not event.is_directory:
            self.organizer.process_file(event.src_path)

class FileOrganizer:
    def __init__(self, config):
        self.config = config
        self.observer = None
        self.event_handler = None

    def start_monitoring(self):
        """Start monitoring the downloads folder"""
        watch_dir = Path(self.config.get('file_organizer.watch_directory')).expanduser()

        if not watch_dir.exists():
            print(f"Watch directory does not exist: {watch_dir}")
            return
        
        self.event_handler = FileOrganizerHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, str(watch_dir), recusrive=False)
        self.observer.start()
        print(f" Started monitoring: {watch_dir}")

    def stop_monitoring(self):
        """Stop file monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            print(" Stopped file monitoring")

    def process_file(self, file_path: str):
        """Process a new file and move it according to rules"""
        try:
            path = Path(file_path)
            if not path.exists() or not path.is_file():
                return
            
            # Wait for file to be completely written
            time.sleep(1)

            extension = path.suffix.lower()
            rules = self.config.get('file_organizer.rules', {})

            for folder, extensions in rules.items():
                if extension in extensions:
                    target_dir = Path(self.config.get('file_organizer.watch_directory')).expanduser().parents / folder
                    target_dir.mkdir(exist_ok=True)
                    target_path = target_dir / path.name

                    # Handle filename conflicts
                    counter = 1
                    while target_path.exists():
                        stem = path.stem
                        target_path = target_dir / f"{stem}_{counter}{path.suffix}"
                        counter += 1

                    path.rename(target_path)
                    print(f" Moved {path.name} to {folder}")
                    break
                
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")