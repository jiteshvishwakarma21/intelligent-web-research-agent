
from modules.summarizer import (
    generate_response,
    summarize_text
)

print("\n--- TEST 1: AI CONNECTION ---")

try:
    answer = generate_response(
        "Explain Artificial Intelligence in five sentences."
    )

    print(answer)

    print("\nAI CONNECTION SUCCESSFUL!")

except RuntimeError as error:
    print(f"ERROR: {error}")


print("\n--- TEST 2: RESEARCH SUMMARY ---")

research_material = """
Artificial Intelligence is transforming education.

AI-powered tools provide personalized learning
experiences to students.

Teachers can use AI to automate administrative
tasks and analyze student performance.

However, AI adoption creates challenges related
to data privacy, digital inequality and
overdependence on technology.
"""

try:
    summary = summarize_text(
        research_material,
        "Impact of Artificial Intelligence on Education"
    )

    print(summary)

    print("\nRESEARCH SUMMARIZATION SUCCESSFUL!")

except RuntimeError as error:
    print(f"ERROR: {error}")
