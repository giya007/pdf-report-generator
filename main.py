import os
import sqlite3
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from pdf_generator import build_html, generate_pdf
from report_queries import get_report_data


app = FastAPI()

DB_NAME = "report.db"
REPORTS_DIR = "reports"


@app.get("/health")
def health():
    return {"status": "ok"}


def get_today_report():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    today = datetime.now().date().isoformat()

    cursor.execute("""
        SELECT id, status, file_path, created_at
        FROM reports
        WHERE DATE(created_at) = ?
        ORDER BY id
        LIMIT 1
    """, (today,))

    report = cursor.fetchone()

    connection.close()

    return report


def create_report_record():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    created_at = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO reports (status, file_path, created_at)
        VALUES (?, ?, ?)
    """, ("generating", None, created_at))

    report_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return report_id


def update_report(report_id, file_path):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE reports
        SET status = ?, file_path = ?
        WHERE id = ?
    """, ("done", file_path, report_id))

    connection.commit()
    connection.close()


def get_report(report_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, status, file_path, created_at
        FROM reports
        WHERE id = ?
    """, (report_id,))

    report = cursor.fetchone()

    connection.close()

    return report


@app.post("/reports", status_code=201)
async def create_report():

    # Check whether today's report already exists
    existing_report = get_today_report()

    if existing_report is not None:
        report_id = existing_report[0]

        return {
            "id": report_id,
            "status": existing_report[1],
            "file": f"/reports/{report_id}/file"
        }

    # Create reports directory
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # Create database record
    report_id = create_report_record()

    # Generate report
    report = get_report_data()

    html = build_html(report)

    file_path = os.path.join(
        REPORTS_DIR,
        f"report_{report_id}.pdf"
    )

    await generate_pdf(html, file_path)

    # Mark report as completed
    update_report(report_id, file_path)

    return {
        "id": report_id,
        "status": "done",
        "file": f"/reports/{report_id}/file"
    }


@app.get("/reports/{report_id}")
def get_report_status(report_id: int):

    report = get_report(report_id)

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    return {
        "id": report[0],
        "status": report[1],
        "file_path": report[2],
        "created_at": report[3],
        "file": f"/reports/{report_id}/file"
        if report[2]
        else None
    }


@app.get("/reports/{report_id}/file")
def download_report(report_id: int):

    report = get_report(report_id)

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    if report[2] is None or not os.path.exists(report[2]):
        raise HTTPException(
            status_code=404,
            detail="Report file not found"
        )

    return FileResponse(
        report[2],
        media_type="application/pdf",
        filename=f"report_{report_id}.pdf"
    )