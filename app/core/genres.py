"""
Genre ID mapping for ua.kinorium.com

Note: These IDs were discovered through API analysis.
If a genre is not found, the scraper will attempt to search by name.
"""

GENRE_MAPPING = {
    "фантастика": "6",
    "комедія": "1",
    "драма": "2",
    "трилер": "3",
    "бойовик": "4",
    "жахи": "5",
    "мелодрама": "7",
    "детектив": "8",
    "пригоди": "9",
    "фентезі": "10",
    "мультфільм": "11",
    "документальний": "12",
    "біографія": "13",
    "історичний": "14",
    "військовий": "15",
    "вестерн": "16",
    "кримінал": "17",
    "мюзикл": "18",
    "сімейний": "19",
    "спорт": "20",
}


def get_genre_id(genre_name: str) -> str:
    """
    Get genre ID by name (case-insensitive).

    Args:
        genre_name: Genre name in Ukrainian

    Returns:
        str: Genre ID or None if not found
    """
    genre_lower = genre_name.lower().strip()
    return GENRE_MAPPING.get(genre_lower)


def get_genre_name(genre_id: str) -> str:
    """
    Get genre name by ID.

    Args:
        genre_id: Genre ID

    Returns:
        str: Genre name or None if not found
    """
    for name, gid in GENRE_MAPPING.items():
        if gid == genre_id:
            return name
    return None


def list_genres():
    """
    Get list of all available genres.

    Returns:
        dict: Mapping of genre names to IDs
    """
    return GENRE_MAPPING.copy()
