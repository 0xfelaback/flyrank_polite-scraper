import requests
import time
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


def exponential_backoff_retry(func, max_retries=3, initial_delay=1, backoff_factor=2):
    retry_count = 0
    delay = initial_delay
    
    while retry_count < max_retries:
        try:
            return func()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Rate limited (429). Retrying in {delay} seconds. (Attempt {retry_count}/{max_retries})")
                    time.sleep(delay)
                    delay *= backoff_factor
                else:
                    print(f"Max retries ({max_retries}) exceeded for 429 error.")
                    raise
            elif e.response.status_code in [404, 503]:
                print(f"HTTP Error {e.response.status_code}: {e}")
                raise
            else:
                raise
        except requests.exceptions.RequestException as e:
            print(f"Request exception: {e}")
            raise


def get_custom_headers():
    return {
        "User-Agent": "PoliteScraperBot/1.0 (+https://github.com/0xfelaback/flyrank_polite-scraper)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }


def rate_limit_delay(min_delay=1, max_delay=3):
    delay = min_delay + (max_delay - min_delay) * 0.5
    time.sleep(delay)


def fetch_page(url, headers=None, check_robots=True, rate_limit=True, min_delay=1, max_delay=3, max_retries=3):
    if headers is None:
        headers = get_custom_headers()
    
    user_agent = headers.get("User-Agent", "PoliteScraperBot/1.0")
    
    if check_robots:
        if not can_fetch_url(user_agent, url):
            print(f"Robots.txt disallows fetching: {url}")
            return None

    def make_request():
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response

    try:
        response = exponential_backoff_retry(make_request, max_retries=max_retries)
        
        if rate_limit:
            rate_limit_delay(min_delay, max_delay)
            
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
        print("\n--- Testing rate limiting with delays ---")
        start_time = time.time()
        
        response = fetch_page(test_url, rate_limit=True, min_delay=1, max_delay=2)

        if response:
            elapsed = time.time() - start_time
            print(f"Request successful!")
            print(f"Status code: {response.status_code}")
            print(f"Time elapsed: {elapsed:.2f}s (includes rate limiting delay)")
        else:
            print("Request failed!")
            
        print("\n--- Testing error handling for 404 ---")
        error_url = "https://httpbin.org/status/404"
        error_response = fetch_page(error_url, rate_limit=False)
        print(f"404 test response: {error_response}")
        
        print("\n--- Testing error handling for 503 ---")
        error_url = "https://httpbin.org/status/503"
        error_response = fetch_page(error_url, rate_limit=False)
        print(f"503 test response: {error_response}")
    else:
        print("\nRequest blocked by robots.txt!")
