import requests
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse


def get_robots_txt_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"


def can_fetch_url(user_agent, url, robots_url=None):
    if robots_url is None:
        robots_url = get_robots_txt_url(url)
    
    rp = RobotFileParser()
    rp.set_url(robots_url)
    
    try:
        rp.read()
        allowed = rp.can_fetch(user_agent, url)
        return allowed
    except Exception as e:
        print(f"Error reading robots.txt: {e}")
        return False


def get_custom_headers():
    return {
        "User-Agent": "PoliteScraperBot/1.0 (+https://github.com/0xfelaback/flyrank_polite-scraper)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }


def fetch_page(url, headers=None, check_robots=True):
    if headers is None:
        headers = get_custom_headers()
    
    user_agent = headers.get("User-Agent", "PoliteScraperBot/1.0")
    
    if check_robots:
        if not can_fetch_url(user_agent, url):
            print(f"Robots.txt disallows fetching: {url}")
            return None

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


if __name__ == "__main__":
    test_url = "https://httpbin.org/user-agent"
    user_agent = "PoliteScraperBot/1.0"

    print(f"Target URL: {test_url}")
    print(f"Custom headers: {get_custom_headers()}")
    
    robots_url = get_robots_txt_url(test_url)
    print(f"Robots.txt URL: {robots_url}")
    
    can_fetch = can_fetch_url(user_agent, test_url)
    print(f"Can fetch {test_url}: {can_fetch}")

    if can_fetch:
        response = fetch_page(test_url)

        if response:
            print(f"\nRequest successful!")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
        else:
            print("\nRequest failed!")
    else:
        print("\nRequest blocked by robots.txt!")
