from kakalot_scraper.scrape.Scraper import scrape_manga

def main():
    url = input("Enter manga URL: ")
    if not url:
        print("No URL provided.")
        return

    print(f"Scraping {url}...")
    images = scrape_manga(url)
    
    print(f"Found {len(images)} images.")
    for i, img in enumerate(images):
        print(f"Showing image {i+1}")
        img.show()

if __name__ == "__main__":
    main()
