import re
from typing import Optional

URL_PATTERN = re.compile(
    r'^(https?|ftp)://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
    r'(?::\d+)?'
    r'(?:/?|[/?]\S+)$',
    re.IGNORECASE
)


def is_valid_url(url: str) -> bool:
    return bool(re.match(URL_PATTERN, url))


def search_engine(query: str, searchable_data: list[str]) -> Optional[list[str]]:
    search_terms = query.split()
    results = []
    for item in searchable_data:
        if all(re.search(re.compile(term, re.IGNORECASE), item) for term in search_terms):
            results.append(item)
    return results if results else None
