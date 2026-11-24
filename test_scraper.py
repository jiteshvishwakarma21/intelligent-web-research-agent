
from modules.search_engine import search_web
from modules.web_scraper import scrape_website


topic = "Impact of Artificial Intelligence on Healthcare"

print("\nSearching for research articles...")

results = search_web(topic, max_results=3)

for index, result in enumerate(results, start=1):

    print(f"\n{'=' * 50}")
    print(f"SOURCE {index}: {result['title']}")
    print(f"URL: {result['url']}")

    print("\nExtracting webpage content...")

    content = scrape_website(result["url"])

    if content:

        print("SCRAPING SUCCESSFUL!")

        print("\nExtracted content preview:")
        print(content[:1000])

        print("\nExtracted characters:", len(content))

    else:

        print("Could not extract webpage content.")

print("\nSCRAPING TEST COMPLETED!")
