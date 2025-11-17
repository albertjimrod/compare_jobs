"""
Utilidades para web scraping.
"""

import random
from typing import Dict, Optional

# Importación opcional de fake_useragent
try:
    from fake_useragent import UserAgent
    HAS_FAKE_UA = True
except ImportError:
    HAS_FAKE_UA = False


class ScrapingUtils:
    """Utilidades comunes para scraping."""

    # User agents comunes
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]

    @staticmethod
    def get_random_user_agent(use_fake_ua: bool = False) -> str:
        """
        Obtiene un user agent aleatorio.

        Args:
            use_fake_ua: Si True, usa fake_useragent library (si está disponible)

        Returns:
            String con user agent
        """
        if use_fake_ua and HAS_FAKE_UA:
            try:
                ua = UserAgent()
                return ua.random
            except Exception:
                # Fallback a lista predefinida
                pass

        return random.choice(ScrapingUtils.USER_AGENTS)

    @staticmethod
    def get_headers(
        referer: Optional[str] = None,
        custom_headers: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Genera headers HTTP para requests.

        Args:
            referer: URL de referencia
            custom_headers: Headers personalizados adicionales

        Returns:
            Diccionario con headers HTTP
        """
        headers = {
            'User-Agent': ScrapingUtils.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }

        if referer:
            headers['Referer'] = referer

        if custom_headers:
            headers.update(custom_headers)

        return headers

    @staticmethod
    def clean_text(text: Optional[str]) -> str:
        """
        Limpia y normaliza texto.

        Args:
            text: Texto a limpiar

        Returns:
            Texto limpio
        """
        if not text:
            return ""

        # Eliminar espacios múltiples
        text = ' '.join(text.split())

        # Eliminar saltos de línea múltiples
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())

        return text.strip()

    @staticmethod
    def extract_salary(text: str) -> Dict[str, Optional[float]]:
        """
        Intenta extraer información salarial del texto.

        Args:
            text: Texto donde buscar información salarial

        Returns:
            Diccionario con salary_min, salary_max, currency
        """
        import re

        result = {
            'salary_min': None,
            'salary_max': None,
            'currency': 'EUR'
        }

        if not text:
            return result

        # Patrones para detectar salarios
        patterns = [
            r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*[-a]\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*[€$]',
            r'[€$]\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*[-a]\s*[€$]\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',
            r'(\d{1,3}(?:[.,]\d{3})*)\s*[-a]\s*(\d{1,3}(?:[.,]\d{3})*)',
        ]

        for pattern in patterns:
            matches = re.search(pattern, text)
            if matches:
                try:
                    min_sal = matches.group(1).replace('.', '').replace(',', '.')
                    max_sal = matches.group(2).replace('.', '').replace(',', '.')

                    result['salary_min'] = float(min_sal)
                    result['salary_max'] = float(max_sal)

                    # Detectar moneda
                    if '$' in text:
                        result['currency'] = 'USD'

                    break
                except (ValueError, IndexError):
                    continue

        return result

    @staticmethod
    def build_search_url(
        base_url: str,
        params: Dict[str, str],
        page: int = 1
    ) -> str:
        """
        Construye una URL de búsqueda con parámetros.

        Args:
            base_url: URL base
            params: Parámetros de búsqueda
            page: Número de página

        Returns:
            URL completa con parámetros
        """
        from urllib.parse import urlencode

        params['page'] = str(page)
        query_string = urlencode(params)

        if '?' in base_url:
            return f"{base_url}&{query_string}"
        else:
            return f"{base_url}?{query_string}"
