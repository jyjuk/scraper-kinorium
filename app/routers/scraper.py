"""
API router for scraping endpoints.
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import (
    FilmsByGenreResponse,
    FilmDetailsResponse,
    BrowserOpenResponse,
    FilmBasic,
    FilmDetails
)
from app.services.improved_scraper import ImprovedScraperService
from app.models.database import get_db
from app.crud import scraping_results
import httpx

router = APIRouter()


@router.get(
    "/scrape/genre",
    response_model=FilmsByGenreResponse,
    summary="Get films by genre using simple HTTP",
    description="Scrapes films by genre using simple HTTP requests without browser automation."
)
async def scrape_films_by_genre(
    genre: str = Query(..., description="Film genre in Ukrainian (e.g., 'комедія', 'драма', 'трилер')"),
    db: AsyncSession = Depends(get_db)
):
    """
    Scrape films by genre using simple HTTP requests.

    - **genre**: Film genre in Ukrainian (e.g., "комедія", "драма", "трилер")

    Returns list of films with title and URL.
    """
    scraper = ImprovedScraperService()

    try:
        films_data = await scraper.scrape_films_by_genre(genre, limit=50)

        films = [FilmBasic(title=f["title"], url=f["url"]) for f in films_data]

        for film_data in films_data:
            try:
                await scraping_results.create_scraping_result(
                    db=db,
                    film_data={
                        "title": film_data["title"],
                        "url": film_data["url"],
                        "genre": genre
                    },
                    scraping_method="http"
                )
            except Exception:
                pass

        return FilmsByGenreResponse(
            genre=genre,
            films=films,
            count=len(films)
        )

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to scrape website: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scraping error: {str(e)}"
        )


@router.get(
    "/scrape/film/details",
    response_model=FilmDetailsResponse,
    summary="Get film details using headless browser",
    description="Scrapes detailed film information using headless browser (Playwright)."
)
async def scrape_film_details(
    film_name: str = Query(..., description="Film name in Ukrainian"),
    db: AsyncSession = Depends(get_db)
):
    """
    Scrape detailed film information using headless browser.

    - **film_name**: Film name to search (in Ukrainian)

    Returns comprehensive film details including rating, genres, cast, etc.
    """
    scraper = ImprovedScraperService()

    try:
        film_details = await scraper.scrape_film_details(film_name)
        scraped_at = datetime.utcnow()

        try:
            await scraping_results.create_scraping_result(
                db=db,
                film_data=film_details,
                scraping_method="headless"
            )
        except Exception:
            pass

        film = FilmDetails(**film_details)

        return FilmDetailsResponse(
            film=film,
            scraped_at=scraped_at,
            scraping_method="headless"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scraping error: {str(e)}"
        )


@router.get(
    "/scrape/film/open-browser",
    response_model=BrowserOpenResponse,
    summary="Open film page in visible browser",
    description="Opens film page in visible browser window (non-headless mode). Note: Works only in local environment, not in Docker."
)
async def open_film_in_browser(
    film_name: str = Query(..., description="Film name in Ukrainian"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Open film page in visible browser window.

    - **film_name**: Film name to search (in Ukrainian)

    Opens the film page in a visible browser window for 30 seconds.

    **Important**: This endpoint requires GUI and will not work in Docker containers.
    Use this only when running the API locally with a display.
    """
    import os

    is_docker = os.path.exists('/.dockerenv') or os.environ.get('RUNNING_IN_DOCKER')

    if is_docker:
        raise HTTPException(
            status_code=501,
            detail="This endpoint is not available in Docker environment. "
                   "Non-headless browser requires GUI which is not available in containers. "
                   "Please use /api/v1/scrape/film/details for headless scraping or run the API locally."
        )

    service = ImprovedScraperService()

    try:
        result = await service.open_film_in_browser(film_name)

        return BrowserOpenResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Browser error: {str(e)}"
        )


@router.get(
    "/results",
    summary="Get scraping history",
    description="Retrieve previously scraped results from database."
)
async def get_scraping_history(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get scraping history from database.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (1-100)

    Returns list of previously scraped films.
    """
    try:
        results = await scraping_results.get_all_scraping_results(
            db=db,
            skip=skip,
            limit=limit
        )

        return {
            "count": len(results),
            "results": [
                {
                    "id": r.id,
                    "film_title": r.film_title,
                    "film_url": r.film_url,
                    "genre": r.genre,
                    "year": r.year,
                    "rating": r.rating,
                    "scraping_method": r.scraping_method,
                    "scraped_at": r.scraped_at
                }
                for r in results
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
