import re


def clean_text(text):
    """
    Clean extracted webpage text
    before sending it to the AI model.
    """

    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove unwanted special characters
    text = re.sub(r"[^\w\s.,;:!?()/%'-]", "", text)

    # Remove duplicate spaces
    text = re.sub(r" +", " ", text)

    return text.strip()


def remove_duplicate_content(texts):
    """
    Remove duplicate research content.
    """

    unique_texts = []
    seen = set()

    for text in texts:
        cleaned = clean_text(text)

        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            unique_texts.append(cleaned)

    return unique_texts