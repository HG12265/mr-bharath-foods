import re

from app.core.exceptions import BaseAppException

MIN_QUERY_LENGTH = 2
MAX_QUERY_LENGTH = 100

def sanitize_query(query: str) -> str:
    """
    Trims and cleans the input query.
    Raises BaseAppException if length constraints are breached.
    """
    cleaned = query.strip()
    if len(cleaned) < MIN_QUERY_LENGTH:
        raise BaseAppException(
            message=f"Search query must be at least {MIN_QUERY_LENGTH} characters.",
            code="QUERY_TOO_SHORT",
            status_code=400
        )
    if len(cleaned) > MAX_QUERY_LENGTH:
        raise BaseAppException(
            message=f"Search query cannot exceed {MAX_QUERY_LENGTH} characters.",
            code="QUERY_TOO_LONG",
            status_code=400
        )
    return cleaned

def generate_typo_regexes(word: str) -> list[str]:
    """
    Generates a list of regex patterns allowing a single character edit distance
    for typo tolerance (substitution).
    """
    # Escaping the word to prevent regex injections
    escaped_word = re.escape(word)
    if len(word) < 3:
        return [escaped_word]

    patterns = [escaped_word]
    # Substitutions: replace each character with '.' wildcard
    for i in range(len(word)):
        prefix = re.escape(word[:i])
        suffix = re.escape(word[i+1:])
        patterns.append(f"{prefix}.{suffix}")

    return patterns

def get_word_search_regex(word: str) -> str:
    """
    Returns a regex pattern string combining the typo tolerance patterns for a word.
    """
    patterns = generate_typo_regexes(word)
    return f"({'|'.join(patterns)})"
