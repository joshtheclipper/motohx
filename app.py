import sqlite3

from flask import Flask, redirect, render_template, request
from flask.ctx import copy_current_request_context

app = Flask(__name__)


# --- DATABASE SETUP ---
def init_db():
    # 1. Connect to the database (this creates 'database.db' if it doesn't exist)
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # 2. Write the SQL to create our table.
    # We add an 'id' column that auto-counts so every record has a unique number.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            service TEXT NOT NULL,
            mileage INTEGER NOT NULL
        )
    """)

    # 3. Save and close
    conn.commit()
    conn.close()


# Run the setup function right away when Python reads this file
init_db()


# --- WEB ROUTES ---
@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":
        new_date = request.form.get("date")
        new_service = request.form.get("service")
        new_mileage = request.form.get("mileage")

        # Connect to DB to save the data
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # We use '?' placeholders instead of variables directly.
        # This is a critical security habit to prevent "SQL Injection" hacking!
        cursor.execute(
            """
            INSERT INTO maintenance (date, service, mileage)
            VALUES (?, ?, ?)
        """,
            (new_date, new_service, new_mileage),
        )
        conn.commit()
        conn.close()
        return redirect("/")

    # IF GET: The user is loading the homepage
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    current_tab = request.args.get("tab", "All")

    # Change our SQL query based on what tab is active
    if current_tab == "All":
        cursor.execute("SELECT * FROM maintenance ORDER BY mileage DESC")
    else:
        cursor.execute(
            "SELECT * FROM maintenance WHERE service = ? ORDER BY mileage DESC",
            (current_tab,),
        )

    records = cursor.fetchall()

    cursor.execute("SELECT DISTINCT service FROM maintenance")
    past_services_rows = cursor.fetchall()
    past_services = [row["service"] for row in past_services_rows]

    default_services = [
        "Oil & Filter Change",
        "Tire Rotation",
        "Wiper Blades Change",
        "Engine Air Filter",
        "Cabin Air Filter",
    ]

    all_options = list(set(default_services + past_services))
    all_options.sort()

    conn.close()

    return render_template(
        "index.html",
        logs=records,
        service_options=all_options,
        tabs=past_services,
        active_tab=current_tab,
    )


@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_record(record_id):
    # 1. Connect to the database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # 2. Run the SQL DELETE command using the ID from the URL
    cursor.execute("DELETE FROM maintenance WHERE id = ?", (record_id,))

    # 3. Commit changes and close
    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
