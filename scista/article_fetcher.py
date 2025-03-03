import requests
import urllib3
import logging
import io
from PyPDF2 import PdfReader

# Настройка логгера
logger = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
__version__ = "0.1.3"
__author__ = "AlestackOverglow"
__email__ = "alestackoverglow@proton.me"
class Article:
    """
    Represents a scientific article with its metadata and content.
    
    Attributes:
        title (str): The title of the article
        doi (str): Digital Object Identifier
        publication_date (str): Publication date
        text (str, optional): Full text or abstract of the article
        pdf_url (str, optional): URL to the PDF version of the article
        url (str, optional): URL to the article webpage
    """
    def __init__(self, title, doi, publication_date, text=None, pdf_url=None, url=None):
        self.title = title
        self.doi = doi
        self.publication_date = publication_date
        self.text = text
        self.pdf_url = pdf_url
        self.url = url

    def save_pdf(self, path):
        """
        Save the article's PDF to a file if available.
        
        Args:
            path (str): Path where to save the PDF file
            
        Returns:
            bool: True if PDF was saved successfully, False otherwise
        """
        if not self.pdf_url:
            logger.warning(f"No PDF for article: {self.title}")
            return False

        try:
            # Set headers for getting PDF
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            # Download file
            response = requests.get(self.pdf_url, headers=headers, allow_redirects=True, verify=False)
            
            # Save PDF
            with open(path, "wb") as f:
                f.write(response.content)
            logger.info(f"PDF saved: {path}")
            return True

        except Exception as e:
            logger.error(f"Error while saving PDF: {str(e)}")
            return False

    def __str__(self):
        return (f"Title: {self.title}\n"
                f"DOI: {self.doi}\n"
                f"Date: {self.publication_date}\n"
                f"Text: {self.text[:200] if self.text else 'No text'}...\n"
                f"URL: {self.url if self.url else 'No URL'}\n"
                f"PDF URL: {self.pdf_url if self.pdf_url else 'No PDF'}")

class ArticleFetcher:
    """
    Main class for fetching scientific articles from various sources.
    
    Args:
        core_api_key (str): API key for CORE
        email_for_unpaywall (str): Email for Unpaywall API access
    """
    def __init__(self, core_api_key, email_for_unpaywall):
        self.core_api_key = core_api_key
        self.email = email_for_unpaywall

    def _get_concept_id(self, category_name):
        concepts_url = f"https://api.openalex.org/concepts?filter=display_name.search:{category_name}"
        try:
            response = requests.get(concepts_url)
            if response.status_code == 200:
                results = response.json().get("results", [])
                if results:
                    return results[0]["id"].replace("https://openalex.org/", "")
                logger.warning(f"Category '{category_name}' not found")
            return None
        except Exception as e:
            logger.error(f"Error while searching for category '{category_name}': {e}")
            return None

    def fetch_articles(self, topic=None, num_articles=5, sort_by_date=True, 
                      categories=None, from_date=None, to_date=None, journals=None):
        """
        Fetch articles based on specified criteria.
        
        Args:
            topic (str, optional): Topic to search for
            num_articles (int, optional): Number of articles to fetch (default: 5)
            sort_by_date (bool, optional): Sort by date descending if True (default: True)
            categories (list or str, optional): Scientific categories to filter by
            from_date (str, optional): Start date in format YYYY-MM-DD
            to_date (str, optional): End date in format YYYY-MM-DD
            journals (list or str, optional): Journal ISSN(s) to filter by
            
        Returns:
            list[Article]: List of found articles
        """
        articles = []
        filters = []
        if topic:
            filters.append(f"title.search:{topic}")
        if categories:
            concept_ids = []
            for cat in categories if isinstance(categories, list) else [categories]:
                if cat.startswith("C") and len(cat) > 5:
                    concept_ids.append(cat)
                else:
                    concept_id = self._get_concept_id(cat)
                    if concept_id:
                        concept_ids.append(concept_id)
            if concept_ids:
                filters.append("concepts.id:" + "|".join(concept_ids))
        if from_date:
            filters.append(f"from_publication_date:{from_date}")
        if to_date:
            filters.append(f"to_publication_date:{to_date}")
        if journals:
            journal_filter = "journal.issn:" + "|".join(journals) if isinstance(journals, list) else journals
            filters.append(journal_filter)

        openalex_url = f"https://api.openalex.org/works?per-page={num_articles}"
        if filters:
            openalex_url += "&filter=" + ",".join(filters)
        if sort_by_date:
            openalex_url += "&sort=publication_date:desc"
        else:
            openalex_url += "&sort=publication_date:asc"

        try:
            response = requests.get(openalex_url)
            if response.status_code == 200:
                results = response.json().get("results", [])
                logger.debug(f"OpenAlex results: {[item['doi'] for item in results]}")
            else:
                logger.error(f"Error while fetching from OpenAlex: status {response.status_code}")
                return articles
        except Exception as e:
            logger.error(f"Error while fetching from OpenAlex: {e}")
            return articles

        for article in results[:num_articles]:
            doi_raw = article.get("doi", "")
            doi = doi_raw.replace("https://doi.org/", "") if doi_raw else None
            title = article.get("title", "No title")
            pub_date = article.get("publication_date", "Unknown")
            
            # Get article URL from OpenAlex
            url = article.get("primary_location", {}).get("landing_page_url") or doi_raw

            text, pdf_url, content_url = self._get_content(title, doi)
            if not text and not pdf_url:
                text = title

            articles.append(Article(
                title=title,
                doi=doi,
                publication_date=pub_date,
                text=text,
                pdf_url=pdf_url,
                url=content_url or url
            ))

        return articles

    def _get_content(self, title, doi):
        """Get article content from available sources."""
        text, pdf_url, url = self._try_core(title)
        if text:  # If text found in CORE
            if doi:  # Check Unpaywall for PDF
                _, unpaywall_pdf, unpaywall_url = self._try_unpaywall(doi)
                if unpaywall_pdf:  # If PDF found in Unpaywall, use it together with text from CORE
                    return text, unpaywall_pdf, unpaywall_url or url
            return text, pdf_url, url  # Otherwise return results from CORE
        
        if doi:  # If text not found in CORE, check Unpaywall
            text, pdf_url, url = self._try_unpaywall(doi)
            if text or pdf_url or url:
                return text, pdf_url, url
                
        return None, None, None

    def _try_core(self, title):
        """Try to get article content from CORE."""
        core_url = f"https://api.core.ac.uk/v3/search/works?q={title}&apiKey={self.core_api_key}"
        try:
            response = requests.get(core_url)
            if response.status_code == 200:
                data = response.json()
                if data.get("results"):
                    result = data["results"][0]
                    full_text = result.get("fullText")
                    pdf_url = result.get("downloadUrl")
                    url = result.get("sourceFulltextUrls", [None])[0] or result.get("sourceUrl")
                    
                    # Check PDF URL for validity
                    if pdf_url:
                        try:
                            headers = {
                                "Accept": "application/pdf",
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                            }
                            head_response = requests.head(pdf_url, headers=headers, allow_redirects=True, verify=False, timeout=5)
                            content_type = head_response.headers.get('content-type', '').lower()
                            
                            if 'pdf' not in content_type and 'octet-stream' not in content_type:
                                logger.warning(f"CORE: Invalid PDF content type: {content_type}")
                                pdf_url = None
                        except Exception as e:
                            logger.warning(f"CORE: Failed to validate PDF URL: {e}")
                            pdf_url = None
                    
                    if full_text:
                        logger.info(f"CORE: Text found for '{title}'")
                    if pdf_url:
                        logger.info(f"CORE: Valid PDF URL found for '{title}'")
                    if url:
                        logger.info(f"CORE: Article URL found for '{title}'")
                    
                    return full_text, pdf_url, url
                    
            logger.debug(f"CORE: Nothing found for '{title}'")
            return None, None, None
        except Exception as e:
            logger.error(f"Error while fetching from CORE: {e}")
            return None, None, None

    def _try_unpaywall(self, doi):
        """Try to get article content from Unpaywall."""
        if not doi:
            return None, None, None
            
        unpaywall_url = f"https://api.unpaywall.org/v2/{doi}?email={self.email}"
        try:
            response = requests.get(unpaywall_url)
            if response and response.status_code == 200:
                data = response.json()
                if not data:
                    logger.debug(f"Unpaywall: No data for DOI {doi}")
                    return None, None, None
                    
                best_oa_location = data.get("best_oa_location", {})
                if not best_oa_location:
                    logger.debug(f"Unpaywall: No open access for DOI {doi}")
                    return None, None, None
                    
                pdf_url = best_oa_location.get("url_for_pdf")
                url = best_oa_location.get("url") or data.get("url")
                text = data.get("abstract")
                
                # Check PDF URL for validity
                if pdf_url:
                    try:
                        headers = {
                            "Accept": "application/pdf",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                        }
                        head_response = requests.head(pdf_url, headers=headers, allow_redirects=True, verify=False, timeout=5)
                        content_type = head_response.headers.get('content-type', '').lower()
                        
                        if 'pdf' not in content_type and 'octet-stream' not in content_type:
                            logger.warning(f"Unpaywall: Invalid PDF content type: {content_type}")
                            pdf_url = None
                    except Exception as e:
                        logger.warning(f"Unpaywall: Failed to validate PDF URL: {e}")
                        pdf_url = None
                
                if pdf_url:
                    logger.info(f"Unpaywall: Valid PDF found for DOI {doi}")
                if url:
                    logger.info(f"Unpaywall: Article URL found for DOI {doi}")
                    
                return text, pdf_url, url
            else:
                logger.error(f"Unpaywall: Error while requesting DOI {doi}, status: {response.status_code if response else 'No response'}")
            return None, None, None
        except Exception as e:
            logger.error(f"Unpaywall: Error: {str(e)}")
            return None, None, None
