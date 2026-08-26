import asyncio
from datetime import date

from playwright.async_api import async_playwright

from report_queries import get_report_data, get_connection


def get_all_books():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT title, price, rating, url
        FROM books
        ORDER BY id
    """)

    books = cursor.fetchall()

    connection.close()

    return books


def build_html(report):
    today = date.today().strftime("%B %d, %Y")

    all_books_rows = ""

    for title, price, rating, url in get_all_books():
        all_books_rows += f"""
        <tr>
            <td>{title}</td>
            <td>£{price:.2f}</td>
            <td>{rating} star</td>
            <td>{url}</td>
        </tr>
        """

    top_books_rows = ""

    for title, price in report["top_5_expensive_books"]:
        top_books_rows += f"""
        <tr>
            <td>{title}</td>
            <td>£{price:.2f}</td>
        </tr>
        """

    rating_rows = ""

    for rating, count in report["books_by_rating"]:
        rating_rows += f"""
        <tr>
            <td>{rating} star</td>
            <td>{count}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">

        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                color: #222;
            }}

            h1 {{
                margin-bottom: 5px;
            }}

            .date {{
                color: #666;
                margin-bottom: 30px;
            }}

            .summary {{
                display: flex;
                gap: 20px;
                margin-bottom: 30px;
            }}

            .card {{
                border: 1px solid #ddd;
                padding: 15px;
                width: 200px;
            }}

            .card h3 {{
                margin: 0 0 10px 0;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                margin-bottom: 30px;
            }}

            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}

            th {{
                background-color: #f2f2f2;
            }}

            thead {{
                display: table-header-group;
            }}

            tr {{
                break-inside: avoid;
                page-break-inside: avoid;
            }}

            .section {{
                margin-top: 30px;
            }}
        </style>
    </head>

    <body>

        <h1>Bookstore Report</h1>

        <div class="date">
            Generated on {today}
        </div>

        <div class="summary">

            <div class="card">
                <h3>Total Books</h3>
                <p>{report["total_books"]}</p>
            </div>

            <div class="card">
                <h3>Average Price</h3>
                <p>£{report["average_price"]:.2f}</p>
            </div>

        </div>

        <div class="section">
            <h2>Top 5 Most Expensive Books</h2>

            <table>
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Price</th>
                    </tr>
                </thead>

                <tbody>
                    {top_books_rows}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>Books by Rating</h2>

            <table>
                <thead>
                    <tr>
                        <th>Rating</th>
                        <th>Number of Books</th>
                    </tr>
                </thead>

                <tbody>
                    {rating_rows}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>All Books</h2>

            <table>
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Price</th>
                        <th>Rating</th>
                        <th>URL</th>
                    </tr>
                </thead>

                <tbody>
                    {all_books_rows}
                </tbody>
            </table>
        </div>

    </body>
    </html>
    """


async def generate_pdf(html, output_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.set_content(html)

        await page.pdf(
            path=output_path,
            format="A4",
            print_background=True
        )

        await browser.close()


if __name__ == "__main__":
    report = get_report_data()

    html = build_html(report)

    with open(
        "report.html",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(html)

    asyncio.run(
        generate_pdf(
            html,
            "reports/test.pdf"
        )
    )

    print("HTML and PDF generated successfully.")