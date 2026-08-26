import sqlite3

DB_NAME = "report.db"


def get_connection():
    return sqlite3.connect(DB_NAME)
def get_total_books():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM books")

    total_books = cursor.fetchone()[0]

    connection.close()

    return total_books
def get_average_price():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT AVG(price) FROM books")

    average_price = cursor.fetchone()[0]

    connection.close()

    return average_price
def get_top_5_expensive_books():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT title, price
        FROM books
        ORDER BY price DESC
        LIMIT 5
    """)

    top_books = cursor.fetchall()

    connection.close()

    return top_books
def get_books_by_rating():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT rating, COUNT(*)
        FROM books
        GROUP BY rating
        ORDER BY rating
    """)

    books_by_rating = cursor.fetchall()

    connection.close()

    return books_by_rating
def get_report_data():
    return {
        "total_books": get_total_books(),
        "average_price": get_average_price(),
        "top_5_expensive_books": get_top_5_expensive_books(),
        "books_by_rating": get_books_by_rating()
    }