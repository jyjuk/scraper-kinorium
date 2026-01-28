"""
Improved scraper service combining reliability with performance.
Uses Playwright with smart waiting and better parsing logic.
"""
import asyncio
from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
from app.core.config import settings


class ImprovedScraperService:
    """Improved scraper using Playwright with better reliability."""

    def __init__(self):
        self.base_url = settings.base_url
        self.timeout = settings.browser_timeout

    async def scrape_films_by_genre(self, genre: str, limit: int = 50) -> List[Dict[str, str]]:
        """
        Scrape films by genre using Playwright.

        Args:
            genre: Genre name in Ukrainian
            limit: Maximum results to return

        Returns:
            List of films with id, title, url
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()

            try:
                await page.goto(self.base_url, timeout=self.timeout, wait_until="domcontentloaded")
                await asyncio.sleep(2)

                search_url = f"{self.base_url}/search/?q={genre}"
                await page.goto(search_url, timeout=self.timeout, wait_until="domcontentloaded")
                await asyncio.sleep(3)

                html = await page.content()

                films = self._parse_film_list(html)

                return films[:limit]

            finally:
                await context.close()
                await browser.close()

    async def scrape_film_details(self, film_name: str) -> Dict[str, Optional[str]]:
        """
        Scrape detailed film information.

        Args:
            film_name: Film name to search

        Returns:
            Dict with film details
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()

            try:
                await page.goto(self.base_url, timeout=self.timeout, wait_until="domcontentloaded")
                await asyncio.sleep(2)

                search_url = f"{self.base_url}/search/?q={film_name}"
                await page.goto(search_url, timeout=self.timeout, wait_until="domcontentloaded")
                await asyncio.sleep(3)

                film_url = await self._find_first_film_link(page)

                if not film_url:
                    raise ValueError(f"Film not found: {film_name}")

                await page.goto(film_url, timeout=self.timeout, wait_until="domcontentloaded")
                await asyncio.sleep(5)

                details = await self._extract_film_details(page)
                details['url'] = film_url

                return details

            finally:
                await context.close()
                await browser.close()

    def _parse_film_list(self, html: str) -> List[Dict[str, str]]:
        """Parse film list from HTML."""
        soup = BeautifulSoup(html, 'lxml')
        films = []

        all_links = soup.find_all('a', href=True)

        for link in all_links:
            href = link.get('href', '')

            if href.startswith('/') and href.count('/') >= 2:
                path_parts = href.strip('/').split('/')
                if path_parts and path_parts[0].isdigit():
                    film_id = path_parts[0]
                    title = link.get_text(strip=True)

                    if title:
                        title = title.replace('топ-500', '').replace('топ-250', '').strip()

                    if title and len(title) > 2:
                        films.append({
                            'id': film_id,
                            'title': title,
                            'url': f"{self.base_url}/{film_id}/"
                        })

        seen_ids = set()
        unique_films = []
        for film in films:
            if film['id'] not in seen_ids:
                seen_ids.add(film['id'])
                unique_films.append(film)

        return unique_films

    async def _find_first_film_link(self, page: Page) -> Optional[str]:
        """Find first film link from search results."""
        links = await page.query_selector_all('a[href]')

        for link in links:
            href = await link.get_attribute('href')
            if href and href.startswith('/'):
                path_parts = href.strip('/').split('/')
                if path_parts and path_parts[0].isdigit():
                    text = await link.inner_text()
                    if text and len(text.strip()) > 2:
                        return f"{self.base_url}{href}"

        return None

    async def _extract_film_details(self, page: Page) -> Dict[str, Optional[str]]:
        """Extract film details from film page."""
        details = {}

        details['title'] = await self._safe_extract(page, ['h1', '.film_title'])

        year_text = await self._safe_extract(page, ['time', '[itemprop="datePublished"]'])
        if year_text:
            import re
            match = re.search(r'\b(19|20)\d{2}\b', year_text)
            details['year'] = int(match.group(0)) if match else None
        else:
            details['year'] = None

        rating_text = await self._safe_extract(page, ['[itemprop="ratingValue"]', '.rating_value'])
        if rating_text:
            import re
            match = re.search(r'(\d+\.?\d*)', rating_text.replace(',', '.'))
            details['rating'] = float(match.group(1)) if match else None
        else:
            details['rating'] = None

        genre_elements = await page.query_selector_all('a[href*="/genre/"]')
        if genre_elements:
            genres = []
            for elem in genre_elements[:5]:
                text = await elem.inner_text()
                if text.strip():
                    genres.append(text.strip())
            details['genres'] = ", ".join(genres) if genres else None
        else:
            details['genres'] = None

        details['director'] = await self._safe_extract(
            page,
            ['[itemprop="director"] [itemprop="name"]', 'a[href*="/name/"]']
        )

        actor_elements = await page.query_selector_all('a[href*="/name/"]')
        if actor_elements:
            actors = []
            for elem in actor_elements[:10]:
                text = await elem.inner_text()
                if text.strip():
                    actors.append(text.strip())
            details['actors'] = ", ".join(actors[:5]) if actors else None
        else:
            details['actors'] = None

        details['duration'] = await self._safe_extract(page, ['[itemprop="duration"]', '.duration'])

        country_elements = await page.query_selector_all('a[href*="/country/"]')
        if country_elements:
            countries = []
            for elem in country_elements[:3]:
                text = await elem.inner_text()
                if text.strip():
                    countries.append(text.strip())
            details['country'] = ", ".join(countries) if countries else None
        else:
            details['country'] = None

        details['description'] = await self._safe_extract(
            page,
            ['[itemprop="description"]', '.film_description', '.description']
        )

        poster_elem = await page.query_selector('[itemprop="image"]')
        if poster_elem:
            src = await poster_elem.get_attribute('src')
            if src:
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = self.base_url + src
                details['poster_url'] = src
        else:
            details['poster_url'] = None

        return details

    async def _safe_extract(self, page: Page, selectors: List[str]) -> Optional[str]:
        """Safely extract text using multiple selectors."""
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    if text and text.strip():
                        return text.strip()
            except Exception:
                continue
        return None

    async def open_film_in_browser(self, film_name: str) -> Dict[str, str]:
        """
        Open film page in visible browser.

        Args:
            film_name: Film name to search

        Returns:
            Dict with status and URL
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, slow_mo=500)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await page.goto(self.base_url, timeout=self.timeout)
                await asyncio.sleep(2)

                search_url = f"{self.base_url}/search/?q={film_name}"
                await page.goto(search_url, timeout=self.timeout)
                await asyncio.sleep(3)

                film_url = await self._find_first_film_link(page)

                if not film_url:
                    raise ValueError(f"Film not found: {film_name}")

                await page.goto(film_url, timeout=self.timeout)

                await asyncio.sleep(30)

                return {
                    "status": "success",
                    "url": film_url,
                    "film_title": film_name,
                    "message": f"Opened film page in browser for 30 seconds"
                }

            finally:
                await context.close()
                await browser.close()
