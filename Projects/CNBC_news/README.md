# CNBC News Summary Project

The CNBC News Summary Project automatically generates a weekly newsletter containing the top business and finance news articles scraped from cnbc.com.

## How it Works

The project utilizes web scraping to gather headlines and descriptions of recent news articles from 5 major sections on the CNBC website:

- Markets
- Business   
- Investing
- Tech
- Politics

The scripts:

1. **news_report_in_txt.py**
   - Scrapes news data from cnbc.com
   - Stores articles in a plaintext file called `news_summary.txt`, organized by section and date

2. **news_report_txt_to_html.py**   
   - Parses the plaintext news summary
   - Generates an HTML report listing all articles alphabetically by company name from A-Z
   - Provides an easy-to-read weekly digest of top business news

## Benefits

- Automatically aggregates the latest news from a trusted source
- Saves time by consolidating content in one place   
- Easy to scan summaries and links to full articles
- Consistent weekly report generation with no manual work
- HTML format makes content viewable on any device

By leveraging web scraping and text processing, the project delivers a convenient weekly newsletter of top CNBC articles for readers.

Let me know if any part of the workflow or markdown formatting needs explanation!