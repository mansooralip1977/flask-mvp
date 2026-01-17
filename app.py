import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "dev-secret-change-me"  # needed for flash messages

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "demo.db")


def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS demo_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                note TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        con.commit()


def get_rows():
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute("""
            SELECT id, name, note, created_at
            FROM demo_entries
            ORDER BY id DESC
            LIMIT 50
        """).fetchall()
    return rows


def insert_row(name: str, note: str):
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            INSERT INTO demo_entries(name, note, created_at)
            VALUES (?, ?, ?)
        """, (name.strip(), note.strip(), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        con.commit()


@app.route("/", methods=["GET", "POST"])
def index():
    init_db()

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        note = (request.form.get("note") or "").strip()

        if not name or not note:
            flash("Please enter both Name and Note.", "error")
            return redirect(url_for("index"))

        insert_row(name, note)
        flash("Saved!", "success")
        return redirect(url_for("index"))

    rows = get_rows()
    return render_template("index.html", rows=rows)


@app.route("/delete/<int:row_id>", methods=["POST"])
def delete(row_id: int):
    init_db()
    with sqlite3.connect(DB_PATH) as con:
        con.execute("DELETE FROM demo_entries WHERE id = ?", (row_id,))
        con.commit()
    flash(f"Deleted row {row_id}.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Runs on http://127.0.0.1:5000
    app.run(debug=True)
