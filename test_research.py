from modules.research_analyzer import conduct_research

topic = "Impact of Artificial Intelligence on Healthcare"

try:

    result = conduct_research(topic, max_results=3)

    print("\n" + "=" * 60)
    print("FINAL RESEARCH REPORT")
    print("=" * 60)

    print("\nTopic:", result["topic"])

    print("\n", result["report"])

    print("\nRESEARCH SOURCES:")

    for source in result["sources"]:
        print("\nTitle:", source["title"])
        print("URL:", source["url"])

    print("\nRESEARCH TEST COMPLETED!")

except Exception as error:
    print("\nERROR:", error)