import requests
import time
import json
import csv
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from bs4 import BeautifulSoup


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


def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup


def extract_elements(soup, selector, attribute=None):
    elements = soup.select(selector)
    
    if attribute:
        return [elem.get(attribute) for elem in elements if elem.get(attribute)]
    else:
        return [elem.get_text(strip=True) for elem in elements]


def extract_element_data(soup, container_selector, data_mapping):
    container = soup.select_one(container_selector)
    if not container:
        return None
    
    extracted_data = {}
    
    for field_name, selector_info in data_mapping.items():
        if isinstance(selector_info, str):
            selector = selector_info
            attribute = None
        else:
            selector = selector_info['selector']
            attribute = selector_info.get('attribute')
        
        element = container.select_one(selector)
        if element:
            if attribute:
                extracted_data[field_name] = element.get(attribute)
            else:
                extracted_data[field_name] = element.get_text(strip=True)
        else:
            extracted_data[field_name] = None
    
    return extracted_data


def structure_scraped_data(url, extracted_data, timestamp=None):
    if timestamp is None:
        from datetime import datetime
        timestamp = datetime.now().isoformat()
    
    structured_data = {
        'url': url,
        'timestamp': timestamp,
        'data': extracted_data
    }
    
    return structured_data


def save_to_json(data, filename='data.json'):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data successfully saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving to JSON: {e}")
        return False


def save_to_csv(data, filename='data.csv'):
    try:
        if not data:
            print("No data to save to CSV")
            return False
        
        if isinstance(data, dict):
            data = [data]
        
        if not data:
            print("Empty data list")
            return False
        
        fieldnames = set()
        for item in data:
            if isinstance(item, dict):
                fieldnames.update(item.keys())
            elif isinstance(item, str):
                fieldnames.add('content')
        
        fieldnames = list(fieldnames)
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in data:
                if isinstance(item, dict):
                    writer.writerow(item)
                elif isinstance(item, str):
                    writer.writerow({'content': item})
        
        print(f"Data successfully saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return False


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
        
        print("\n--- Testing HTML parsing with BeautifulSoup ---")
        html_test_url = "https://httpbin.org/html"
        html_response = fetch_page(html_test_url, rate_limit=False)
        
        if html_response:
            print(f"HTML fetch successful! Status: {html_response.status_code}")
            
            soup = parse_html(html_response.text)
            print(f"Parsed HTML with BeautifulSoup. Title: {soup.title.string if soup.title else 'No title'}")
            
            print("\n--- Testing element extraction ---")
            h1_elements = extract_elements(soup, 'h1')
            print(f"H1 elements found: {h1_elements}")
            
            links = extract_elements(soup, 'a', attribute='href')
            print(f"Link hrefs found: {links}")
            
            print("\n--- Testing structured data extraction ---")
            data_mapping = {
                'title': 'h1',
                'description': 'p',
            }
            extracted_data = extract_element_data(soup, 'body', data_mapping)
            print(f"Extracted structured data: {extracted_data}")
            
            print("\n--- Testing data structuring ---")
            structured_data = structure_scraped_data(html_test_url, extracted_data)
            print(f"Structured data: {structured_data}")
            
            print("\n--- Testing JSON export ---")
            json_success = save_to_json(structured_data, 'data.json')
            print(f"JSON export success: {json_success}")
            
            print("\n--- Testing CSV export ---")
            csv_success = save_to_csv([structured_data], 'data.csv')
            print(f"CSV export success: {csv_success}")
            
            print("\n--- Testing multiple items CSV export ---")
            multiple_items = [
                structure_scraped_data(html_test_url, {'title': 'Test 1', 'description': 'Description 1'}),
                structure_scraped_data(html_test_url, {'title': 'Test 2', 'description': 'Description 2'}),
            ]
            csv_multi_success = save_to_csv(multiple_items, 'data_multiple.csv')
            print(f"Multiple items CSV export success: {csv_multi_success}")
        else:
            print("HTML fetch failed!")
    else:
        print("\nRequest blocked by robots.txt!")
