# i2i Academy - Web Scraping & ETL Pipelines 

This repository contains a standalone, end-to-end Data Engineering pipeline built natively in Python. The project demonstrates a complete ETL (Extract, Transform, Load) workflow interacting with containerized infrastructure via Docker.

# Project Architecture & Scope

The pipeline independently extracts raw, unstructured data from a target website, cleans and structures it using data analysis libraries, and reliably loads it into a relational database.

1. **Extraction (Web Scraper):** Utilizes `requests` and `BeautifulSoup` to programmatically harvest product details (Title, Price, and Star Rating) from a public catalog website (`books.toscrape.com`).
2. **Transformation (Data Cleaning):** Loads the raw scraped data into a `Pandas` DataFrame. It comprehensively cleans the data by parsing text-based currency strings into float values, converting string ratings into standardized integers, handling missing entries, and appending execution timestamps.
3. **Loading (Database Storage):** Establishes a connection to a containerized `PostgreSQL` instance running inside Docker using `SQLAlchemy`. The data is safely written into a structured SQL table.
4. **Idempotency Logic:** Includes an upsert mechanism (`ON CONFLICT DO UPDATE`) based on the Primary Key (`title`) to ensure that multiple script executions do not produce duplicate entries or compromise data integrity.
5. **Logging:** Operational summaries and row counts are printed directly to the terminal upon successful execution.


