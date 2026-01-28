# Kinorium Scraper API

Asynchronous REST API service for scraping film information from [ua.kinorium.com](https://ua.kinorium.com) using FastAPI, Playwright, and SQLAlchemy.

## Features

- **Three scraping methods**:
  1. HTTP-based scraping (fast, no browser overhead)
  2. Headless browser scraping (Playwright - comprehensive data)
  3. Non-headless browser mode (visible window for debugging)

- **Async architecture** - Built with FastAPI and async/await for high performance
- **Database integration** - SQLAlchemy with async support (SQLite/PostgreSQL)
- **Data validation** - Pydantic schemas for request/response validation
- **Docker support** - Ready-to-deploy containerized application
- **API documentation** - Auto-generated OpenAPI/Swagger docs

## Tech Stack

- **Python 3.11+**
- **FastAPI** - Modern async web framework
- **Playwright** - Browser automation library
- **SQLAlchemy** - Async ORM with aiosqlite
- **Pydantic** - Data validation
- **BeautifulSoup4** - HTML parsing
- **httpx** - Async HTTP client

## Project Structure

```
Scraper/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── core/
│   │   ├── config.py           # Configuration management
│   │   └── genres.py           # Genre mappings
│   ├── models/
│   │   ├── database.py         # Database setup
│   │   ├── models.py           # SQLAlchemy models
│   │   └── schemas.py          # Pydantic schemas
│   ├── routers/
│   │   └── scraper.py          # API endpoints
│   ├── services/
│   │   └── improved_scraper.py # Scraping logic
│   └── crud/
│       └── scraping_results.py # Database operations
├── .env.example                # Environment variables template
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
├── requirements.txt
└── run.py                      # Local server startup script
```

## Quick Start

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Scraper
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs

**Note**: The non-headless browser endpoint (#3) is disabled in Docker as it requires GUI.

### Option 2: Local Development

1. **Clone and setup environment**
   ```bash
   git clone <repository-url>
   cd Scraper
   cp .env.example .env
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Run the server**
   ```bash
   python run.py
   ```

   **Windows users**: The `run.py` script includes Windows-specific event loop configuration required for Playwright. Auto-reload is disabled on Windows for compatibility.

5. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs

## API Endpoints

### 1. Scrape Films by Genre

Scrape films using HTTP requests (no browser automation).

**Endpoint:** `GET /api/v1/scrape/genre`

**Parameters:**
- `genre` (string, required) - Genre name in Ukrainian (e.g., "комедія", "драма", "трилер")

**Example:**
```bash
curl "http://localhost:8000/api/v1/scrape/genre?genre=комедія"
```

**Response:**
```json
{
  "genre": "комедія",
  "films": [
    {
      "title": "Film Title",
      "url": "https://ua.kinorium.com/12345/"
    }
  ],
  "count": 50
}
```

### 2. Get Film Details

Scrape detailed film information using headless browser.

**Endpoint:** `GET /api/v1/scrape/film/details`

**Parameters:**
- `film_name` (string, required) - Film name to search (in Ukrainian)

**Example:**
```bash
curl "http://localhost:8000/api/v1/scrape/film/details?film_name=Леон"
```

**Response:**
```json
{
  "film": {
    "title": "Леон",
    "url": "https://ua.kinorium.com/100515/",
    "year": 1994,
    "rating": 8.5,
    "genres": "Трилер, Драма, Кримінал",
    "director": "Люк Бессон",
    "actors": "Жан Рено, Наталі Портман, Ґері Олдман",
    "country": "Франція, США",
    "duration": "110 хв",
    "description": "Professional assassin Leon...",
    "poster_url": "https://..."
  },
  "scraped_at": "2026-01-28T...",
  "scraping_method": "headless"
}
```

### 3. Open in Browser (Local Only)

Open film page in visible browser window (non-headless mode).

**Endpoint:** `GET /api/v1/scrape/film/open-browser`

**Parameters:**
- `film_name` (string, required) - Film name to search

**Example:**
```bash
curl "http://localhost:8000/api/v1/scrape/film/open-browser?film_name=Леон"
```

**Note:** This endpoint only works in local environment with GUI. Returns 501 error in Docker.

### 4. Get Scraping History

Retrieve previously scraped results from database.

**Endpoint:** `GET /api/v1/results`

**Parameters:**
- `skip` (integer, optional) - Number of records to skip (default: 0)
- `limit` (integer, optional) - Maximum records to return (default: 10, max: 100)

## Configuration

All configuration is managed through environment variables in `.env` file:

```env
# Application settings
APP_NAME=Kinorium Scraper API
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Database settings
DATABASE_URL=sqlite+aiosqlite:///./scraper.db

# Scraping settings
REQUEST_TIMEOUT=30
BROWSER_TIMEOUT=60000
HEADLESS_MODE=True

# Target website
BASE_URL=https://ua.kinorium.com
```

## Database

The application uses SQLite by default. To use PostgreSQL:

1. Update `DATABASE_URL` in `.env`:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
   ```

2. Install asyncpg:
   ```bash
   pip install asyncpg
   ```

## Development

### Running Tests

The project uses manual testing scripts. To test all endpoints:

```bash
# Test endpoint 1 (Genre)
curl "http://localhost:8000/api/v1/scrape/genre?genre=комедія"

# Test endpoint 2 (Details)
curl "http://localhost:8000/api/v1/scrape/film/details?film_name=Титанік"

# Test endpoint 3 (Browser - local only)
curl "http://localhost:8000/api/v1/scrape/film/open-browser?film_name=Леон"
```

### Code Style

- All code comments are in English
- Search supports Ukrainian language
- Follow PEP 8 style guidelines
- Use type hints for all functions

## Important Notes

### Windows Compatibility

When running locally on Windows, the server uses a special startup script (`run.py`) that:
- Sets the Windows event loop policy for Playwright compatibility
- Disables auto-reload mode (required for subprocess support)
- Configures asyncio loop explicitly

**To apply code changes on Windows**: Manually restart the server.

### Docker Limitations

- The non-headless browser endpoint (#3) is disabled in Docker
- This is expected behavior as Docker containers don't have GUI
- Use endpoints #1 and #2 in Docker environment

## License

This project is for educational purposes only.

## Support

For issues and questions, please open an issue on GitHub.

---

**Built with using FastAPI and Playwright**
