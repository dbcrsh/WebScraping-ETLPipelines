import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text

def run_etl():

    print("[LOG] Starting Extraction...")
    url = "http://books.toscrape.com/catalogue/category/books_1/index.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    books = soup.find_all('article', class_='product_pod')
    raw_data = []

    for book in books:
        title = book.h3.a['title']
        price_str = book.find('p', class_='price_color').text
        rating_class = book.p['class'][1]  # Extracts string like 'Three', 'One'
        
        raw_data.append({
            'title': title, 
            'price': price_str, 
            'rating': rating_class
        })

    print(f"[LOG] Extracted {len(raw_data)} raw items from the target website.")

  
    print("[LOG] Starting Transformation...")
    df = pd.DataFrame(raw_data)

    # Clean Price: Remove currency symbols and non-numeric characters, cast to float
    df['price'] = df['price'].str.replace(r'[^\d.]', '', regex=True).astype(float)

    # Clean Rating: Map string ratings to actual integers
    rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    df['rating'] = df['rating'].map(rating_map)

    # Add execution timestamp
    df['extracted_at'] = datetime.now()

    print("[LOG] Transformation complete. Data is cleaned and structured.")


    print("[LOG] Starting Database Load...")
    
    # Dockerized PostgreSQL connection details
    DB_USER = "admin"
    DB_PASS = "admin123"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "i2i_etl"

    engine = create_engine(f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

    # Create table if it doesn't exist. Title is the PRIMARY KEY for idempotency.
    create_table_query = """
    CREATE TABLE IF NOT EXISTS scraped_books (
        title VARCHAR PRIMARY KEY,
        price FLOAT,
        rating INTEGER,
        extracted_at TIMESTAMP
    );
    """

    # Upsert Query (Idempotency logic: Update if exists, insert if new)
    insert_query = text("""
    INSERT INTO scraped_books (title, price, rating, extracted_at)
    VALUES (:title, :price, :rating, :extracted_at)
    ON CONFLICT (title) DO UPDATE 
    SET price = EXCLUDED.price, 
        rating = EXCLUDED.rating, 
        extracted_at = EXCLUDED.extracted_at;
    """)

    try:
        with engine.begin() as conn:
            # Execute table creation
            conn.execute(text(create_table_query))
            
            # Execute inserts/updates row by row
            processed_rows = 0
            for record in df.to_dict(orient='records'):
                conn.execute(insert_query, record)
                processed_rows += 1
                
        print(f"[LOG] ETL Pipeline Finished Successfully! {processed_rows} rows safely upserted into the database.")
        
    except Exception as e:
        print(f"[ERROR] Database operation failed: {e}")

if __name__ == "__main__":
    run_etl()