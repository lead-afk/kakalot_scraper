from kakalot_scraper.scrape.Scraper import scrape_manga
from kakalot_scraper.cbz.Generator import *
from kakalot_scraper.manager.Manager import *


class Settings:
    SAVE_ROOT = "./manga"


def scrape_manga_and_save(url: str, full_reset: bool = False):

    chapters = get_chapters_list(url=url)
    print(f"Found {len(chapters)} chapters.")
    for chapter_num, chapter_url in chapters:
        print(f"Chapter {chapter_num}: {chapter_url}")
    print("Waiting before fetching manga info...")
    time.sleep(5)

    manga_info = get_manga_info(url=url)
    print(f"Manga Information:")
    print(manga_info)
    print("Waiting before processing chapters...")
    time.sleep(5)

    full_reset = False
    ret_count = 0
    i = 0
    while i < len(chapters):
        (chapter_num, chapter_url) = chapters[i]

        cbz_path = get_cbz_path(manga_info, chapter_num, Settings.SAVE_ROOT)
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
        generate_cbz(manga_info, chapter_num, images, Settings.SAVE_ROOT)

        ret_count = 0
        i += 1

        print("Waiting 15 seconds before next chapter...")
        time.sleep(15)
        break


def main():
    scrape_manga_and_save(
        "https://www.mangakakalot.gg/manga/akuyaku-no-goreisoku-no-dounika-shitai-nichijou"
    )


if __name__ == "__main__":
    main()
