# Kakalot Scraper

A robust Python-based tool designed to scrape manga chapters specifically from [mangakakalot.gg](https://www.mangakakalot.gg) and convert them into CBZ (Comic Book Zip) format for easy reading. By default configured for intergration with Komga, but can be used standalone as well.

## Features

- **Targeted Scraping**: Optimized for `mangakakalot.gg`.
- **CBZ Conversion**: Automatically compiles downloaded images into CBZ files.
- **Image Filtering**: Removes unwanted images (e.g., ads, watermarks) from the final CBZ.
- **Metadata Extraction**: Gathers and includes relevant metadata (e.g., title, author, tags, genres, etc.) in the CBZ file.
- **Batch Processing**: Scrape multiple manga series automatically using a configuration file.
- **Smart Resume**: Skips chapters that have already been downloaded to save time and bandwidth.
- **Retry Mechanism**: Handles network hiccups and rate limits with automatic retries.
- **Full Reset Option**: Force re-download of all chapters if needed.
- **Docker Support**: Easily deployable via Docker for consistent environments.
- **Service Mode**: Can run as a long-lived service that watches for changes in the configuration file to trigger new scrapes and periodically checks for updates to watched manga series.

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd kakalot_scraper
   ```

2. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   This tool uses Playwright for scraping. You need to install the necessary browser binaries:
   ```bash
   playwright install
   ```

## Docker Usage

You can also run the scraper using Docker, which handles all dependencies for you.

### Docker Compose Example

`Note that before running the container, you should create and populate the to_scrape.conf file in the docker directory with the manga URLs you want to scrape, or at least create it as an empty file to avoid errors.`

```yaml
services:
  scraper:
    image: leadafk/kakalot_scraper:latest
    container_name: kakalot_scraper
    volumes:
      - ./to_scrape.conf:/app/to_scrape.conf
      - ./manga:/app/manga
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "/app/healthcheck.sh"]
      interval: 10m
      timeout: 30s
      retries: 3
```

### Prerequisites

- Docker
- Docker Compose

### Running with Docker Compose

1. **Configure URLs:**
   Add the manga URLs you want to scrape to `to_scrape.conf`.

2. **Build and Run:**
   Navigate to the docker directory and run:

   ```bash
   cd docker
   docker-compose up --build
   ```

   The scraper will start processing the URLs in `to_scrape.conf`. The downloaded manga will be available in the `manga/` directory on your host machine.

### Running Manually with Docker

If you prefer to run specific commands (like scraping a single URL):

1. **Build the image:**

   ```bash
   docker build -t kakalot-scraper .
   ```

2. **Run a single scrape:**
   ```bash
   docker run -v $(pwd)/manga:/app/manga kakalot-scraper --url https://www.mangakakalot.gg/manga/manga-title
   ```

## Usage

### 1. Batch Scraping (Default)

To scrape multiple manga series, add their URLs to the `to_scrape.conf` file (one URL per line).

**Example `to_scrape.conf`:**

```text
https://www.mangakakalot.gg/manga/another-manga-title
```

Then run the script:

```bash
python main.py
```

### 2. Scrape a Single Manga

You can scrape a specific manga directly via the command line, bypassing the configuration file:

```bash
python main.py --url https://www.mangakakalot.gg/manga/manga-title
```

### 3. Force Re-download

To force a re-download of all chapters (ignoring existing files), use the `--full-reset` flag:

```bash
python main.py --full-reset
# OR with a specific URL
python main.py --url https://www.mangakakalot.gg/manga/manga-title --full-reset
```

## Output

Downloaded chapters are saved in the `manga/` directory in the root of the project.
Structure:

```
manga/
    Manga Title/
        chapter_001_0_Manga_Title.cbz
        chapter_002_0_Manga_Title.cbz
        ...
```

## Disclaimer

This tool is for educational purposes only. Please respect the copyright of the manga creators and publishers as well as TOS of [mangakakalot.gg](https://www.mangakakalot.gg). Use this tool responsibly and do not overload the target website.

`This scraper was not developed with reference to any official documentation or guidelines from mangakakalot.gg. Consequently, it may break if the website structure changes.`

## Notes

- Ensure you have permission to download and use the manga content.
- Due to full browser rendering, scraping may take longer than traditional HTML parsing methods, also the RAM usage will be higher, the scraper may use upwards of `4GB` of RAM for large manga series.

## License

GNU General Public License v3.0 or later (GPL-3.0-or-later)
