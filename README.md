# Polite Web Scraper

A Python web scraper that respects website conventions and follows ethical scraping practices.

## Project Overview

This scraper fetches web pages while honoring robots.txt rules, implementing rate limiting, and extracting structured data cleanly. It is designed to be respectful to target servers and compliant with web standards.

## Ethical Scraping Guidelines

This scraper follows these ethical practices:

- **Custom User-Agent**: Identifies itself clearly as `PoliteScraperBot/1.0` with contact information
- **Robots.txt Compliance**: Checks and honors robots.txt rules before making requests
- **Rate Limiting**: Implements delays between requests (1-3 seconds by default)
- **Error Handling**: Gracefully handles HTTP errors with exponential backoff for rate limits
- **Respectful Access**: Does not overwhelm servers with rapid requests

## Installation

### Requirements

- Python 3.12 or higher
- Poetry (for dependency management)

### Setup

1. Clone the repository:

```bash
git clone https://github.com/0xfelaback/flyrank-polite-scraper.git
cd flyrank-polite-scraper
```

1. Install dependencies using Poetry:

```bash
poetry install
```

Alternatively, install dependencies manually:

```bash
pip install requests beautifulsoup4 urllib3
```

## Execution

Run the scraper with the included test suite:

```bash
poetry run python src/scraper.py
```

Or without Poetry:

```bash
python3 src/scraper.py
```

## Usage

The scraper provides several functions for web scraping:

### Basic Usage

```python
from src.scraper import fetch_page, parse_html, extract_elements, save_to_json

# Fetch a page
response = fetch_page("https://example.com")

# Parse HTML
soup = parse_html(response.text)

# Extract elements
titles = extract_elements(soup, 'h1')
links = extract_elements(soup, 'a', attribute='href')

# Save to JSON
data = {'titles': titles, 'links': links}
save_to_json(data, 'output.json')
```

### Advanced Usage

```python
from src.scraper import (
    fetch_page, parse_html, extract_element_data,
    structure_scraped_data, save_to_csv
)

# Fetch and parse
response = fetch_page("https://example.com", rate_limit=True)
soup = parse_html(response.text)

# Extract structured data
data_mapping = {
    'title': 'h1',
    'description': 'p.description',
    'author': 'span.author'
}
extracted = extract_element_data(soup, 'article', data_mapping)

# Structure and export
structured = structure_scraped_data("https://example.com", extracted)
save_to_csv([structured], 'output.csv')
```

## Features

- **Custom Headers**: Descriptive User-Agent string
- **Robots.txt Parsing**: Uses Python's `urllib.robotparser`
- **Rate Limiting**: Configurable delays between requests
- **Exponential Backoff**: Handles 429 errors with retry logic
- **HTML Parsing**: BeautifulSoup integration
- **Data Export**: JSON and CSV output formats
- **Error Handling**: Graceful handling of 404, 429, and 503 errors

## Sample Output

### JSON Output

```json
{
  "url": "https://httpbin.org/html",
  "timestamp": "2026-09-03T04:44:00.000000",
  "data": {
    "title": "Herman Melville - Moby-Dick",
    "description": "Avast ye scurvy dogs!"
  }
}
```

### CSV Output

```csv
url,timestamp,data.title,data.description
https://httpbin.org/html,2026-09-03T04:44:00.000000,Herman Melville - Moby-Dick,Avast ye scurvy dogs!
```

## Configuration

### Rate Limiting

Adjust delays between requests:

```python
response = fetch_page(url, min_delay=2, max_delay=5)
```

### Retry Behavior

Configure retry attempts for rate limiting:

```python
response = fetch_page(url, max_retries=5)
```

### Robots.txt Check

Disable robots.txt checking if needed (not recommended):

```python
response = fetch_page(url, check_robots=False)
```

## Project Structure

```
flyrank-polite-scraper/
├── src/
│   └── scraper.py
├── pyproject.toml         
├── poetry.lock            
└── README.md            
```