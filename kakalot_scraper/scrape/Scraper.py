from PIL import Image
from io import BytesIO
from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Page

class SETTINGS:
    MINIMUM_IMAGE_WIDTH = 200
    MINIMUM_IMAGE_HEIGHT = 300
    DIV_CLASS_NAME = "container-chapter-reader"

def scrape_manga(manga_url: str, ignore_url_issues: bool = False) -> list[Image.Image]:
    
    parts = manga_url.split("/")
    if len(parts) < 3 and not ignore_url_issues:
        print(f"Invalid URL: {manga_url}")
        return []

    domain, tmp, manga_name, chapter_id = parts[2:6]

    chapter_id = chapter_id.split("-")[1] if chapter_id and "-" in chapter_id else chapter_id

    try:
        chapter_id = int(chapter_id) if chapter_id else None
    except ValueError:
        chapter_id = None

    if (not manga_name or not chapter_id) and not ignore_url_issues:
        print(f"Invalid manga URL: {manga_url}")
        return []

    if not manga_url.startswith("http") and not ignore_url_issues:
        print(f"Invalid URL: {manga_url}")
        return []

    valid_images: list[tuple[Image.Image, str]] = []

    with sync_playwright() as p:
        # Launch browser (headless=True is faster, but False is better for debugging/stealth)
        browser = p.chromium.launch(headless=True)
        
        # Create a context with a real user agent
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page: Page = context.new_page()
        
        # Store intercepted image data
        captured_images = {}

        def handle_response(response):
            try:
                if response.request.resource_type == "image":
                    captured_images[response.url] = response.body()
            except Exception:
                pass

        page.on("response", handle_response)

        try:
            print(f"Navigating to {manga_url}...")
            page.goto(manga_url, wait_until="domcontentloaded")
            
            # Wait for the container to appear (handles JS loading)
            try:
                page.wait_for_selector(f".{SETTINGS.DIV_CLASS_NAME}", timeout=30000)
            except Exception:
                print("Timeout waiting for content container. The page might not have loaded correctly or the class name changed.")
                browser.close()
                return []
            
            # Scroll to bottom to trigger lazy loading
            print("Scrolling to load images...")
            page.evaluate("""
                async () => {
                    await new Promise((resolve) => {
                        let totalHeight = 0;
                        const distance = 100;
                        const timer = setInterval(() => {
                            const scrollHeight = document.body.scrollHeight;
                            window.scrollBy(0, distance);
                            totalHeight += distance;

                            if(totalHeight >= scrollHeight){
                                clearInterval(timer);
                                resolve();
                            }
                        }, 100);
                    });
                }
            """)
            
            # Wait for network to settle
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass

            # Find all images in the container
            container = page.locator(f".{SETTINGS.DIV_CLASS_NAME}")
            images = container.locator("img").all()
            
            print(f"Found {len(images)} potential images.")

            for img in images:
                src = img.get_attribute("src")
                if not src:
                    continue
                
                try:
                    # Try to get from captured responses first
                    image_data = captured_images.get(src)
                    
                    if not image_data:
                        print(f"Image {src} not found in captured responses, trying fallback...")
                        # Fallback: Try to fetch using page context if not captured
                        response = page.request.get(src)
                        if response.status == 200:
                            image_data = response.body()
                    
                    if image_data:
                        image = Image.open(BytesIO(image_data))
                        
                        if (image.width >= SETTINGS.MINIMUM_IMAGE_WIDTH and 
                            image.height >= SETTINGS.MINIMUM_IMAGE_HEIGHT):
                            valid_images.append((image, src))
                    else:
                        print(f"Could not retrieve data for {src}")

                except Exception as e:
                    print(f"Error processing image {src}: {e}")
                    continue

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.close()

    for i, (img, src) in enumerate(valid_images):
        print(f"Valid image {i+1}: {src} ({img.width}x{img.height})")

    filtered_images: list[Image.Image] = []
    
    for img, src in valid_images:
        if manga_name in src:
            filtered_images.append(img)

    return filtered_images if len(filtered_images) > 0 else [img for img, _ in valid_images]

if __name__ == "__main__":
    test_url = "https://www.mangakakalot.gg/manga/akuyaku-no-goreisoku-no-dounika-shitai-nichijou/chapter-26"
    images = scrape_manga(test_url)
    print(f"Scraped {len(images)} valid images.")
    
    for i, img in enumerate(images):
        print(f"Showing image {i+1}")
        img.show()
        a = input("Press Enter to continue or 'q' to quit: ")
        if a == "q":
            break
