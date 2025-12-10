# Copilot Instructions for Kakalot Scraper

This document provides context and guidelines for AI agents working on the `kakalot_scraper` codebase.

## 1. Project Overview & Architecture

This is a Python-based manga scraper specifically targeted at `mangakakalot.gg`. It uses **Playwright** for browser automation to handle dynamic content and lazy loading.

### Core Components

- **`main.py`**: The entry point and orchestrator. Handles argument parsing, the main scraping loop, and the "self-service" watchdog mode.
- **`kakalot_scraper/scrape/Scraper.py`**: Contains the core scraping logic. It uses Playwright to intercept network requests for images rather than just parsing HTML `src` attributes.
- **`kakalot_scraper/manager/Manager.py`**: Responsible for fetching manga metadata (title, author, status) and the list of chapters.
- **`kakalot_scraper/cbz/Generator.py`**: Handles the creation of `.cbz` (Comic Book Zip) files from downloaded images.
- **`kakalot_scraper/watchdog/Watchdog.py`**: Implements file system monitoring to trigger scrapes when `to_scrape.conf` is modified.

### Data Flow

1.  **Input**: URLs are read from `to_scrape.conf` or command-line args.
2.  **Discovery**: `Manager` fetches chapter links and manga info.
3.  **Scraping**: `Scraper` navigates to each chapter, scrolls to trigger lazy loading, and intercepts image responses.
4.  **Output**: `Generator` compiles images into a CBZ file in the `manga/` directory.

## 2. Critical Developer Workflows

### Running the Scraper

- **Local**: `python main.py` (requires `playwright install` first).
- **Docker**: `docker compose up --build`. This is the preferred production method.

### Service Mode & Watchdog

- The application has a "self-service" mode (`--self-service`) designed for long-running container execution.
- It watches `to_scrape.conf` for changes using `watchdog`.
- **Healthcheck**: It writes a timestamp to a `./heartbeat` file. The `healthcheck.sh` script monitors this file to ensure the service is alive.

### Configuration

- **`to_scrape.conf`**: A simple text file with one manga URL per line.
- **`kakalot_scraper/__init__.py`**: Contains global constants like `SAVE_ROOT` and `BASE_URL`.

## 3. Coding Conventions & Patterns

### Playwright Usage

- **Sync API**: The project uses `sync_playwright`.
- **Network Interception**: We prefer intercepting `response` events to capture image data directly from the network stream. This bypasses issues with protected or complex `src` URLs.
  ```python
  # Example pattern from Scraper.py
  def handle_response(response):
      if response.request.resource_type == "image":
          captured_images[response.url] = response.body()
  page.on("response", handle_response)
  ```
- **Lazy Loading**: The scraper explicitly scrolls the page to trigger lazy-loaded images.

### File Naming

- CBZ files follow a strict naming convention: `chapter_{number}_{safe_title}.cbz`.
- Use `kakalot_scraper.cbz.Generator.generate_file_chapter_name` for consistency.

### Docker

- The `Dockerfile` sets `ENV PYTHONUNBUFFERED=1` to ensure logs are visible in real-time.
- The build context in `docker-compose.yml` is set to `..` (parent dir) to include source code while keeping docker files in `docker/`.

## 4. Common Tasks

- **Adding a new site**: This scraper is specialized for `mangakakalot.gg`. Adapting it for other sites would require significant changes to `Scraper.py` and `Manager.py` selectors.
- **Debugging Scraper**: If images aren't loading, check `Scraper.py`. You may need to adjust the `wait_for_selector` timeout or the scrolling logic. Setting `headless=False` in `playwright.launch()` helps visualize the issue.
