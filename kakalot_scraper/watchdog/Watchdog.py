from watchdog.events import FileSystemEventHandler
import kakalot_scraper
import threading
import os

wake_up_event = threading.Event()


class Handler(FileSystemEventHandler):
    def trigger_scrape(self):
        print("File change detected, triggering scrape...")
        global wake_up_event
        wake_up_event.set()

    def _is_target_file(self, path):
        # Normalize paths to ensure accurate comparison
        print(f"Detected file event on: {path}")
        target_path = os.path.abspath(kakalot_scraper.GLOBAL.URL_LIST_FILE_PATH)
        event_path = os.path.abspath(path)
        return event_path == target_path

    def on_created(self, event):
        print(f"File created: {event.src_path}")
        if self._is_target_file(event.src_path):
            self.trigger_scrape()

    def on_modified(self, event):
        print(f"File modified: {event.src_path}")
        if self._is_target_file(event.src_path):
            self.trigger_scrape()

    def on_moved(self, event):
        print(f"File moved: {event.src_path} to {event.dest_path}")
        if self._is_target_file(event.src_path) or self._is_target_file(
            event.dest_path
        ):
            self.trigger_scrape()
