"""
CRUD operations for scraping results.
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import ScrapingResult


async def create_scraping_result(
    db: AsyncSession,
    film_data: dict,
    scraping_method: str
) -> ScrapingResult:
    """
    Create new scraping result in database.

    Args:
        db: Database session
        film_data: Dictionary with film information
        scraping_method: Method used for scraping (http, headless, browser)

    Returns:
        ScrapingResult: Created database record
    """
    result = ScrapingResult(
        film_title=film_data.get("title", ""),
        film_url=film_data.get("url"),
        genre=film_data.get("genre"),
        year=film_data.get("year"),
        rating=film_data.get("rating"),
        director=film_data.get("director"),
        actors=film_data.get("actors"),
        duration=film_data.get("duration"),
        country=film_data.get("country"),
        description=film_data.get("description"),
        poster_url=film_data.get("poster_url"),
        genres=film_data.get("genres"),
        scraping_method=scraping_method
    )
    db.add(result)
    await db.commit()
    await db.refresh(result)
    return result


async def get_scraping_result_by_id(
    db: AsyncSession,
    result_id: int
) -> Optional[ScrapingResult]:
    """
    Get scraping result by ID.

    Args:
        db: Database session
        result_id: Result ID

    Returns:
        Optional[ScrapingResult]: Found result or None
    """
    result = await db.execute(
        select(ScrapingResult).where(ScrapingResult.id == result_id)
    )
    return result.scalar_one_or_none()


async def get_scraping_results_by_title(
    db: AsyncSession,
    title: str,
    limit: int = 10
) -> List[ScrapingResult]:
    """
    Get scraping results by film title.

    Args:
        db: Database session
        title: Film title to search
        limit: Maximum number of results

    Returns:
        List[ScrapingResult]: List of matching results
    """
    result = await db.execute(
        select(ScrapingResult)
        .where(ScrapingResult.film_title.ilike(f"%{title}%"))
        .order_by(ScrapingResult.scraped_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_scraping_results_by_genre(
    db: AsyncSession,
    genre: str,
    limit: int = 50
) -> List[ScrapingResult]:
    """
    Get scraping results by genre.

    Args:
        db: Database session
        genre: Film genre
        limit: Maximum number of results

    Returns:
        List[ScrapingResult]: List of matching results
    """
    result = await db.execute(
        select(ScrapingResult)
        .where(ScrapingResult.genre.ilike(f"%{genre}%"))
        .order_by(ScrapingResult.scraped_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_all_scraping_results(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[ScrapingResult]:
    """
    Get all scraping results with pagination.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of results

    Returns:
        List[ScrapingResult]: List of results
    """
    result = await db.execute(
        select(ScrapingResult)
        .order_by(ScrapingResult.scraped_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())
