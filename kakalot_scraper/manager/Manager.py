import time
from typing import Any
from playwright.sync_api import sync_playwright


def is_ongoing(manga: str) -> bool:
    """
    Determines if the manga at the given URL is ongoing.

    Args:
        manga (str): The URL of the manga page.

    Returns:
        bool: True if the manga is ongoing, False otherwise.
    """
    div_class_name = "manga-info-text"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(manga)
            # Wait for the element to be present to ensure the page is loaded enough
            page.wait_for_selector(f".{div_class_name}", timeout=5000)

            elements = page.locator(f".{div_class_name}").all()
            for element in elements:
                if "Status : Ongoing" in element.inner_text():
                    return True
        except Exception as e:
            print(f"Error checking status: {e}")
        finally:
            browser.close()

    return False


def get_manga_name(url: str):

    manga_name = url.strip("/").split("/")[4]
    return manga_name


class MangaInfo:
    def __init__(
        self,
        title: str,
        author: str,
        status: str,
        last_updated: str,
        views: str,
        genres: list[str],
        rating: str,
        url: str,
    ):
        self.title = title
        self.author = author
        self.status = status
        self.last_updated = last_updated
        self.views = views
        self.genres = genres
        self.rating = rating
        self.url = url

    def __repr__(self):
        return (
            f"Title: {self.title}\n"
            f"Author: {self.author}\n"
            f"Status: {self.status}\n"
            f"Last Updated: {self.last_updated}\n"
            f"Views: {self.views}\n"
            f"Genres: {', '.join(self.genres)}\n"
            f"Rating: {self.rating}\n"
            f"URL: {self.url}"
        )

    def healthcheck(self) -> bool:
        print(
            f"Performing healthcheck for manga: {self.title}, last updated: {self.last_updated}"
        )
        if self.title == "Unknown" and self.last_updated == "Unknown":
            print("Healthcheck failed: Title and Last Updated are Unknown")
            return False
        print("Healthcheck passed")
        return True


def get_manga_info(url: str) -> MangaInfo:
    """
    Retrieves information about the manga at the given URL.

    Args:
        url (str): The URL of the manga page.

    Returns:
        MangaInfo: An object containing manga information.
    """
    title = get_manga_name(url)
    author = "Unknown"
    status = "Unknown"
    last_updated = "Unknown"
    views = "Unknown"
    genres: list[str] = []
    rating = "Unknown"

    div_class_name = "manga-info-text"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url)
            page.wait_for_selector(f".{div_class_name}", timeout=5000)

            container = page.locator(f".{div_class_name}")

            # Title
            if container.locator("h1").count() > 0:
                title = container.locator("h1").inner_text().strip()

            # Iterate through li elements to find specific info
            lis = container.locator("li").all()
            for li in lis:
                text = li.inner_text()
                if "Author(s) :" in text:
                    author = text.replace("Author(s) :", "").strip()
                elif "Status :" in text:
                    status = text.replace("Status :", "").strip()
                elif "Last updated :" in text:
                    last_updated = text.replace("Last updated :", "").strip()
                elif "View :" in text:
                    views = text.replace("View :", "").strip()
                elif "Genres :" in text:
                    genres = [a.inner_text().strip() for a in li.locator("a").all()]

            # Rating
            rating_elem = container.locator("#rate_row_cmd")
            if rating_elem.count() > 0:
                rating = rating_elem.inner_text().strip()

        except Exception as e:
            print(f"Error getting manga info: {e}")
        finally:
            browser.close()

    return MangaInfo(
        title=title,
        author=author,
        status=status,
        last_updated=last_updated,
        views=views,
        genres=genres,
        rating=rating,
        url=url,
    )


def chapter_rename(chapter_text: str) -> str:
    chapter = chapter_text.lower().replace("chapter", "").strip()

    try:
        chapter_num = int(chapter)
        formatted = f"{chapter_num:04d}" + "_0"
        return formatted
    except ValueError:
        pass

    try:
        chapter_num = float(chapter)
        formatted = f"{chapter_num:06.1f}".replace(".", "_")
        return formatted
    except ValueError:
        pass

    return chapter.replace(" ", "_")


def get_chapters_list(url: str) -> list[tuple[str, str]]:
    """
    Retrieves the list of chapter URLs for the manga at the given URL.

    Args:
        url (str): The URL of the manga page.

    Returns:
        list[tuple[str, str]]: A list of tuples (chapter number, chapter_url).
    """
    chapter_urls: list[tuple[str, str]] = []
    div_class_name = "chapter-list"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url)
            page.wait_for_selector(f".{div_class_name}", timeout=5000)

            rows = page.locator(f".{div_class_name} .row").all()

            for row in rows:
                link = row.locator("a").first
                if link.count() > 0:
                    href = link.get_attribute("href")
                    text = link.inner_text()

                    # Extract chapter number, assuming format "Chapter X"
                    chapter_num = chapter_rename(text)

                    if href:
                        chapter_urls.append((chapter_num, href))

        except Exception as e:
            print(f"Error getting chapters: {e}")
        finally:
            browser.close()

    return chapter_urls


if __name__ == "__main__":
    test_url = "https://www.mangakakalot.gg/manga/akuyaku-no-goreisoku-no-dounika-shitai-nichijou"

    manga_info = get_manga_info(test_url)
    print(f"Manga Information:")
    print(manga_info)
    print("Waiting before fetching chapters...")
    time.sleep(5)

    chapters = get_chapters_list(test_url)
    print(f"Found {len(chapters)} chapters:")
    for chapter_num, chapter_url in chapters:
        print(f"Chapter {chapter_num}: {chapter_url}")
