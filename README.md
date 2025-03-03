# Scista

Scista - Python library for searching and downloading scientific articles from various sources, including OpenAlex, CORE and Unpaywall.

## Functionality

- Search for articles by topic, category and date
- Get article metadata (title, authors, DOI, etc.)
- Download full texts and PDF versions of articles
- Support for multiple data sources

## Installation

```bash
pip install scista
```

## Requirements

- Python 3.7+
- API key for CORE (get it on [CORE API](https://core.ac.uk/services/api))
- Email for Unpaywall (any email, no registration needed)


## Search Filters

The library provides several optional search filters that can be used individually or in combination:

```python
articles = fetcher.fetch_articles(
    topic="quantum computing",     # Search by topic in title
    num_articles=5,               # Number of articles to fetch (default: 5)
    categories=["Physics"],       # Filter by scientific categories
    from_date="2023-01-01",      # Start date (format: YYYY-MM-DD)
    to_date="2023-12-31",        # End date (format: YYYY-MM-DD)
    sort_by_date=True,           # Sort by date (newest first if True)
    journals=["1234-5678"]       # Filter by journal ISSN(s)
)
```

All filters are optional. You can use any combination of them:

```python
# Search only by topic
articles = fetcher.fetch_articles(topic="quantum computing")

# Search by category and date range
articles = fetcher.fetch_articles(
    categories=["Physics"],
    from_date="2023-01-01",
    to_date="2023-12-31"
)

# Get latest articles from specific journals
articles = fetcher.fetch_articles(
    journals=["1234-5678", "8765-4321"],
    sort_by_date=True,
    num_articles=10
)
```

### Filter Details

- `topic`: Search for articles with this topic in the title
- `num_articles`: Maximum number of articles to fetch (default: 5)
- `categories`: Scientific categories to filter by. Can be a single category or a list
- `from_date`: Start date in YYYY-MM-DD format
- `to_date`: End date in YYYY-MM-DD format
- `sort_by_date`: If True, sorts by date descending (newest first)
- `journals`: Filter by journal ISSN(s). Can be a single ISSN or a list

## Return Values

The `fetch_articles()` method returns a list of `Article` objects. Each `Article` object contains:

```python
class Article:
    title: str            # Title of the article
    doi: str             # Digital Object Identifier
    publication_date: str # Publication date in YYYY-MM-DD format
    text: str | None     # Full text or abstract (if available)
    pdf_url: str | None  # URL to download PDF (if available)
```

### Example of returned data:

```python
articles = fetcher.fetch_articles(topic="quantum computing", num_articles=1)
article = articles[0]

print(article)
# Output:
# Title: Quantum Computing: A New Era of Computation
# DOI: 10.1234/example.doi.2023
# Date: 2023-12-25
# Text: This paper explores the fundamentals of quantum computing...
# PDF URL: https://example.com/article.pdf

# Access individual fields
print(article.title)           # Get article title
print(article.doi)            # Get DOI
print(article.publication_date)# Get publication date
print(article.text)           # Get full text/abstract
print(article.pdf_url)        # Get PDF URL

# Save PDF if available
if article.pdf_url:
    article.save_pdf("article.pdf")
```

### Notes about returned data:

- `text`: Can contain either full text (from CORE) or abstract (from Unpaywall)
- `pdf_url`: URL for PDF download, available if article is found in CORE or Unpaywall
- `doi`: May be None for some articles
- `publication_date`: Always provided, but format may vary depending on source
- Articles are returned in order specified by `sort_by_date` parameter

## Methods

### Article class methods

#### save_pdf(path: str) -> bool
Saves the article's PDF to a file if available.

```python
article = articles[0]
success = article.save_pdf("article.pdf")
if success:
    print("PDF successfully saved")
else:
    print("Failed to save PDF or PDF not available")
```

Parameters:
- `path`: Path where to save the PDF file

Returns:
- `bool`: True if PDF was saved successfully, False if PDF is not available or there was an error

Error handling:
- Returns False if PDF URL is not available
- Returns False if download fails (HTTP error)
- Returns False if file cannot be written
- Logs appropriate error messages through the logging system

## Usage

```python
import logging
from scista import ArticleFetcher

# Configure logging (optional)
logging.basicConfig(
    level=logging.INFO,  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize with your API keys
fetcher = ArticleFetcher(
    core_api_key="your_core_api_key",
    email_for_unpaywall="your_email@example.com"
)

# Search for articles
articles = fetcher.fetch_articles(
    topic="quantum computing",  # Topic to search
    num_articles=5,            # Number of articles
    categories=["Physics"],    # Category
    from_date="2023-01-01",   # Start date
    to_date="2023-12-31",     # End date
    sort_by_date=True         # Sort by date
)

# Process results
for i, article in enumerate(articles, 1):
    print(f"\nArticle {i}:")
    print(article)
    
    # Save PDF if available
    if article.pdf_url:
        article.save_pdf(f"article_{i}.pdf")
```

## Logging

The library uses the standard `logging` Python module. You can configure logging to your needs:

```python
import logging

# Basic configuration
logging.basicConfig(
    level=logging.INFO,  # Logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Or more complex configuration
logger = logging.getLogger('scista')
handler = logging.FileHandler('scista.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
```

Logging levels:
- DEBUG: Detailed debug information
- INFO: Confirmation of successful operations
- WARNING: Warnings about potential problems
- ERROR: Errors that do not interrupt the program
- CRITICAL: Critical errors

## License

MIT License

## Author

AlestackOverglow
