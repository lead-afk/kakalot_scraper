import os
import kakalot_scraper
from urllib.parse import urlparse
import time
import tqdm as tqdm


def sleep_seconds(seconds: int) -> None:
    for _ in tqdm.tqdm(range(seconds), desc="Waiting", unit="s"):
        time.sleep(1)


def check_paths() -> None:
    print("Checking necessary paths and files...")
    if not os.path.exists(kakalot_scraper.GLOBAL.SAVE_ROOT):
        try:
            os.makedirs(kakalot_scraper.GLOBAL.SAVE_ROOT)
        except OSError:
            print(f"Error creating directory: {kakalot_scraper.GLOBAL.SAVE_ROOT}")
            return

    if not os.path.exists(kakalot_scraper.GLOBAL.URL_LIST_FILE_PATH):
        print(f"URL list file not found: {kakalot_scraper.GLOBAL.URL_LIST_FILE_PATH}")
        return


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])


def load_urls_from_file(file_path: str) -> list[str]:
    if not os.path.exists(file_path):
        print(f"URL list file not found: {file_path}")
        return []

    with open(file_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    lines = list(set(lines))  # Remove duplicates

    for line in lines:
        if not is_valid_url(line):
            print(f"Invalid URL in list, skipping: {line}")
            lines.remove(line)

    return lines
