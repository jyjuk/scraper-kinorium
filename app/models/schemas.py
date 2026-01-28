"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl


class FilmBasic(BaseModel):
    """Basic film information from genre search."""

    title: str = Field(..., description="Film title")
    url: str = Field(..., description="Film page URL")


class FilmsByGenreResponse(BaseModel):
    """Response for films by genre endpoint."""

    genre: str = Field(..., description="Requested genre")
    films: List[FilmBasic] = Field(default_factory=list, description="List of films")
    count: int = Field(..., description="Number of films found")


class FilmDetails(BaseModel):
    """Detailed film information from scraping."""

    title: str = Field(..., description="Film title")
    url: Optional[str] = Field(None, description="Film page URL")
    year: Optional[int] = Field(None, description="Release year")
    rating: Optional[float] = Field(None, description="Film rating")
    genres: Optional[str] = Field(None, description="Film genres")
    director: Optional[str] = Field(None, description="Director name")
    actors: Optional[str] = Field(None, description="Main actors")
    duration: Optional[str] = Field(None, description="Film duration")
    country: Optional[str] = Field(None, description="Country of production")
    description: Optional[str] = Field(None, description="Film description")
    poster_url: Optional[str] = Field(None, description="Poster image URL")


class FilmDetailsResponse(BaseModel):
    """Response for film details endpoint."""

    film: Optional[FilmDetails] = Field(None, description="Film details")
    scraped_at: datetime = Field(..., description="Scraping timestamp")
    scraping_method: str = Field(..., description="Method used for scraping")


class BrowserOpenResponse(BaseModel):
    """Response for browser open endpoint."""

    status: str = Field(..., description="Operation status")
    url: Optional[str] = Field(None, description="Opened URL")
    film_title: str = Field(..., description="Film title searched")
    message: str = Field(..., description="Status message")


class ErrorResponse(BaseModel):
    """Error response schema."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    app_name: str = Field(..., description="Application name")
    version: str = Field(default="1.0.0", description="API version")
