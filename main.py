import kakalot_scraper
from kakalot_scraper.manager.Manager import MangaInfo
from kakalot_scraper.scrape.Scraper import scrape_manga
from kakalot_scraper.cbz.Generator import *
from kakalot_scraper.manager.Manager import *
from kakalot_scraper.utils.Utils import *

from kakalot_scraper.watchdog.Watchdog import Handler, wake_up_event
from watchdog.observers.polling import PollingObserver as Observer

import time
import argparse
import os


def scrape_manga_and_save(url: str, full_reset: bool = False):
    print(f"Scraping manga from URL: {url}")
    chapters: list[tuple[str, str]] = get_chapters_list(url=url)
    chapters.reverse()
    print(f"Found {len(chapters)} chapters.")
    for chapter_num, chapter_url in chapters:
        print(f"Chapter {chapter_num}: {chapter_url}")
    print("Waiting before fetching manga info...")

    time.sleep(10)

    fail_count = 0
    while True:
        manga_info: MangaInfo = get_manga_info(url=url)
        print("Fetched manga info, performing healthcheck...")
        if manga_info.healthcheck():
            break
        fail_count += 1
        if fail_count >= 3:
            print("Maximum retries reached. Exiting.")
            return
        print("Manga info healthcheck failed, retrying in 20 seconds...")
        time.sleep(20)

    print(f"Manga Information:")
    print(manga_info)
    print("Waiting before processing chapters...")
    time.sleep(10)

    full_reset = False
    ret_count = 0
    i = 0
    while i < len(chapters):
        (chapter_num, chapter_url) = chapters[i]

        cbz_path = get_cbz_path(
            manga_info, chapter_num, kakalot_scraper.GLOBAL.SAVE_ROOT
        )
        if os.path.exists(cbz_path) and not full_reset:
            print(f"Chapter {chapter_num} already exists, skipping...")
            i += 1
            continue

        print(f"Chapter {chapter_num}: {chapter_url}")
        images = scrape_manga(chapter_url)
        if not images:
            print(
                f"No valid images found for Chapter {chapter_num}, assuming rate limit."
            )
            print("Waiting 15 seconds before retrying...")
            time.sleep(15)
            ret_count += 1
            if ret_count >= 3:
                print("Maximum retries reached. Exiting.")
                break
            i -= 1
            continue

        print(f"Scraped {len(images)} valid images for Chapter {chapter_num}.")
        generate_cbz(manga_info, chapter_num, images, kakalot_scraper.GLOBAL.SAVE_ROOT)

        ret_count = 0
        i += 1

        print("Waiting 15 seconds before next chapter...")
        time.sleep(15)


def scrape_all(full_reset: bool = False) -> None:
    urls = load_urls_from_file(kakalot_scraper.GLOBAL.URL_LIST_FILE_PATH)
    print(f"Loaded {len(urls)} URLs to process.")
    if not urls or len(urls) == 0:
        print("No valid URLs to process.")
        return

    for url in urls:
        print(f"Processing Manga: {url}")
        scrape_manga_and_save(url, full_reset)


def self_service_mode() -> None:

    global wake_up_event
    observer = Observer()
    observer.schedule(Handler(), path=".", recursive=False)
    observer.start()

    print("Self-service mode started. Watching for changes in configuration file.")

    # Create heartbeat immediately so healthcheck passes
    with open("./heartbeat", "w") as f:
        f.write(str(time.time()))

    try:
        while True:
            scrape_all()
            print("Scrape cycle complete. Waiting for next trigger or timeout...")
            # Wait for 1 hour or until wake_up_event is set
            # We check every 10 minutes to update heartbeat
            for _ in range(6):
                if wake_up_event.wait(timeout=600):
                    print("Wake up event received!")
                    wake_up_event.clear()
                    break

                # Update heartbeat
                with open("./heartbeat", "w") as f:
                    f.write(str(time.time()))

            # If we exited the loop because of the event, we loop back to scrape_all immediately
            # If we exited because the range finished (1 hour passed), we also loop back to scrape_all

    except KeyboardInterrupt:
        print("Stopping self-service mode...")
    finally:
        observer.stop()
        observer.join()


def main() -> None:

    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="URL of the manga to scrape")
    parser.add_argument(
        "--full-reset",
        action="store_true",
        help="Re-download all chapters",
        default=False,
    )
    parser.add_argument(
        "--self-service", action="store_true", help="Enable self-service mode"
    )
    args = parser.parse_args()

    check_paths()

    if args.self_service:
        self_service_mode()
        return

    if args.url:
        scrape_manga_and_save(args.url, args.full_reset)
        return

    print("No URL provided, proceeding to scrape all URLs from the list.")
    scrape_all(args.full_reset)


if __name__ == "__main__":
    print("Kakalot Scraper started.")
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
