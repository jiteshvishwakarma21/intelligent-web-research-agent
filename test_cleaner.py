from modules.text_cleaner import (
    clean_text,
    remove_duplicate_content
)

sample_text = """
    Artificial Intelligence   is transforming healthcare.

    AI helps doctors   improve diagnosis.
"""

print("Original Text:")
print(sample_text)

cleaned = clean_text(sample_text)

print("\nCleaned Text:")
print(cleaned)

sample_data = [
    "Artificial Intelligence improves healthcare.",
    "Artificial Intelligence improves healthcare.",
    "AI helps doctors diagnose diseases."
]

unique_data = remove_duplicate_content(sample_data)

print("\nAfter Removing Duplicate Content:")

for item in unique_data:
    print("-", item)

print("\nTEXT CLEANING TEST COMPLETED!")