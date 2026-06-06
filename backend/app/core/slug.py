import re


def slugify(text: str) -> str:
    """
    Converts input text to a URL-safe lowercase slug format.
    """
    text = text.lower().strip()
    # Remove all non-word characters (except spaces and hyphens)
    text = re.sub(r"[^\w\s-]", "", text)
    # Replace spaces, underscores, and multiple hyphens with a single hyphen
    text = re.sub(r"[\s_-]+", "-", text)
    return text
