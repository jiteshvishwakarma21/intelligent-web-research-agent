
from modules.search_engine import search_web


topic = "Impact of Artificial Intelligence on Healthcare"

print("\nSearching the web...")
print("Research Topic:", topic)

try:

    results = search_web(topic, max_results=5)

    for index, result in enumerate(results, start=1):

        print(f"\n--- SOURCE {index} ---")

        print("Title:", result["title"])
        print("URL:", result["url"])
        print("Description:", result["snippet"])

    print("\nWEB SEARCH COMPLETED!")

except RuntimeError as error:

    print("ERROR:", error)
