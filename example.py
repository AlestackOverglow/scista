import logging
from scista import ArticleFetcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    # Initialize with your API keys
    fetcher = ArticleFetcher(core_api_key="your_core_api", email_for_unpaywall="any_email")
    
    # Example search for articles
    articles = fetcher.fetch_articles(
        num_articles=10,            # Number of articles
        categories=["Physics"],    # Category
        to_date="2024-12-31",     # End date
        sort_by_date=True         # Sort by date (newest first)
    )
    
    # Output results and save PDF
    for i, article in enumerate(articles, 1):
        print(f"\nArticle {i}:")
        print(article)
        
        # Save PDF if available
        if article.pdf_url:
            article.save_pdf(f"article_{i}.pdf")

if __name__ == "__main__":
    main() 