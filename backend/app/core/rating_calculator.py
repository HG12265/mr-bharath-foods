from typing import Any


def calculate_ratings_summary(reviews: list[dict[str, Any]] | list[Any]) -> dict[str, Any]:
    """
    Given a list of Review model/dict items, returns a dictionary containing
    the computed average, total count, and individual star frequencies.
    """
    total = len(reviews)
    star_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    total_stars = 0

    for item in reviews:
        # Support both model objects (having .rating) and raw dicts (having ["rating"])
        if hasattr(item, "rating"):
            rating = item.rating
        elif isinstance(item, dict):
            rating = item.get("rating", 0)
        else:
            rating = 0

        if 1 <= rating <= 5:
            star_counts[rating] += 1
            total_stars += rating

    average = round(total_stars / total, 2) if total > 0 else 0.0

    return {
        "average_rating": average,
        "review_count": total,  # For backward compatibility
        "total_reviews": total,
        "star_1_count": star_counts[1],
        "star_2_count": star_counts[2],
        "star_3_count": star_counts[3],
        "star_4_count": star_counts[4],
        "star_5_count": star_counts[5],
    }
