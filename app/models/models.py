"""
SQLAlchemy database models.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from app.models.database import Base


class ScrapingResult(Base):
    """Model for storing scraping results."""

    __tablename__ = "scraping_results"

    id = Column(Integer, primary_key=True, index=True)
    film_title = Column(String(500), nullable=False, index=True)
    film_url = Column(String(1000), nullable=True)
    genre = Column(String(200), nullable=True, index=True)
    year = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True)
    director = Column(String(500), nullable=True)
    actors = Column(Text, nullable=True)
    duration = Column(String(100), nullable=True)
    country = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    poster_url = Column(String(1000), nullable=True)
    genres = Column(String(500), nullable=True)
    scraping_method = Column(String(50), nullable=False)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ScrapingResult(id={self.id}, title='{self.film_title}', method='{self.scraping_method}')>"
