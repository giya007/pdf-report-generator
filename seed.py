import sqlite3
import json

DB_NAME = "report.db"
BOOKS_FILE = "books.json"


def create_database():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            rating INTEGER NOT NULL,
            url TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def seed_books():
    with open(BOOKS_FILE, "r", encoding="utf-8") as file:
        books = json.load(file)

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    # Clear existing records before inserting
    cursor.execute("DELETE FROM books")

    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    for book in books:
        title = book["title"]
        price = book["price_gbp"]
        rating = rating_map[book["rating_text"]]
        url = book["product_url"]

        cursor.execute("""
            INSERT INTO books (title, price, rating, url)
            VALUES (?, ?, ?, ?)
        """, (title, price, rating, url))

    connection.commit()

    cursor.execute("SELECT COUNT(*) FROM books")
    count = cursor.fetchone()[0]

    connection.close()

    print(f"Inserted {count} books.")


if __name__ == "__main__":
    create_database()
    seed_books()