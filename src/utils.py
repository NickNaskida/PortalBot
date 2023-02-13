import requests
from typing import Optional

from urllib3.util.retry import Retry


def request_url(url: str, headers: Optional[dict] = None) -> requests.Response:
    """
    Request URL.
    :param url: URL to request
    :param headers: HTTP headers
    :return: Response object
    """
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session.get(url, headers=headers)


def format_prices(prices: dict) -> str:
    """
    Format prices.
    :param prices: Prices dict
    :return: Formatted prices
    """

    return "\n".join([f"{fuel} - *{price}*" for fuel, price in prices.items()])


def format_price(price: float) -> float:
    """
    Format price.
    :param price: Price
    :return: Formatted price
    """
    return "{:.2f}".format(abs(round(price, 2)))
