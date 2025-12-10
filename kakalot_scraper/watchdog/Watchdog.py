from watchdog.events import FileSystemEventHandler
import kakalot_scraper
import threading
import os

wake_up_event = threading.Event()


class Handler(FileSystemEventHandler):
    def trigger_scrape(self):
        print("File change detected, triggering scrape...")
        wake_up_event.set()

    def _is_target_file(self, path):
        # Normalize paths to ensure accurate comparison
        target_path = os.path.abspath(kakalot_scraper.GLOBAL.URL_LIST_FILE_PATH)
        event_path = os.path.abspath(path)
        return event_path == target_path

    def on_created(self, event):
        if self._is_target_file(event.src_path):
            self.trigger_scrape()

    def on_modified(self, event):
        if self._is_target_file(event.src_path):
            self.trigger_scrape()

    def on_moved(self, event):
        if self._is_target_file(event.src_path):
            self.trigger_scrape()
