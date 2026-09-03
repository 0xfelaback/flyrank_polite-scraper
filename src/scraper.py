import requests


def get_custom_headers():
    return {
        "User-Agent": "PoliteScraperBot/1.0 (+https://github.com/0xfelaback/flyrank_polite-scraper)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }


def fetch_page(url, headers=None):
    if headers is None:
        headers = get_custom_headers()

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


if __name__ == "__main__":
    test_url = "https://httpbin.org/user-agent"

    print(f"Target URL: {test_url}")
    print(f"Custom headers: {get_custom_headers()}")

    response = fetch_page(test_url)

    if response:
        print(f"\nRequest successful!")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
    else:
        print("\nRequest failed!")
