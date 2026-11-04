
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, Response, jsonify
)
from functools import wraps
import pandas as pd
import sqlite3
import json
import os
import io
import secrets
from pathlib import Path
from datetime import datetime


app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    secrets.token_hex(32)
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "dataset" / "library_data.csv"
DB_PATH = BASE_DIR / "library.db"


# =====================================
# DATABASE CONNECTION
# =====================================

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# =====================================
# DATABASE INITIALIZATION
# =====================================

def init_db():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            Book_ID TEXT PRIMARY KEY,
            Book_Title TEXT NOT NULL,
            Author TEXT NOT NULL,
            Category TEXT NOT NULL,
            Book_Origin TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            Loan_ID TEXT PRIMARY KEY,
            Book_ID TEXT NOT NULL,
            Issue_Date TEXT NOT NULL,
            Due_Date TEXT NOT NULL,
            Return_Date TEXT,
            Loan_Status TEXT NOT NULL
                CHECK (Loan_Status IN ('Returned', 'Active', 'Overdue')),
            FOREIGN KEY (Book_ID) REFERENCES books(Book_ID)
        )
    """)

    conn.commit()

    book_count = cursor.execute(
        "SELECT COUNT(*) FROM books"
    ).fetchone()[0]

    # Import CSV only when database has no books
    if book_count == 0 and DATA_PATH.exists():

        data = pd.read_csv(DATA_PATH)

        for _, row in data.iterrows():

            book_id = str(row["Book_ID"]).strip()

            cursor.execute("""
                INSERT OR IGNORE INTO books
                (Book_ID, Book_Title, Author, Category, Book_Origin)
                VALUES (?, ?, ?, ?, ?)
            """, (
                book_id,
                str(row["Book_Title"]).strip(),
                str(row["Author"]).strip(),
                str(row["Category"]).strip(),
                str(row["Book_Origin"]).strip()
            ))

            return_date = (
                None if pd.isna(row["Return_Date"])
                else str(row["Return_Date"])[:10]
            )

            cursor.execute("""
                INSERT OR IGNORE INTO loans
                (Loan_ID, Book_ID, Issue_Date, Due_Date,
                 Return_Date, Loan_Status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(row["Loan_ID"]).strip(),
                book_id,
                str(row["Issue_Date"])[:10],
                str(row["Due_Date"])[:10],
                return_date,
                str(row["Loan_Status"]).strip()
            ))

        conn.commit()

    conn.close()


init_db()


# =====================================
# LOGIN PROTECTION
# =====================================

def login_required(route_function):

    @wraps(route_function)
    def wrapper(*args, **kwargs):

        if not session.get("librarian_logged_in"):
            flash(
                "Please login to access the Admin Panel.",
                "error"
            )
            return redirect(url_for("login"))

        return route_function(*args, **kwargs)

    return wrapper


# =====================================
# LIBRARIAN LOGIN
# =====================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if session.get("librarian_logged_in"):
        return redirect(url_for("admin"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        correct_email = os.environ.get(
            "LIBRARIAN_EMAIL", ""
        ).strip().lower()

        correct_password = os.environ.get(
            "LIBRARIAN_PASSWORD", ""
        )

        if not correct_email or not correct_password:
            flash("Login credentials are not configured.", "error")
            return render_template("login.html")

        if not email.endswith("@gmail.com"):
            flash("A complete @gmail.com address is required.", "error")
            return render_template("login.html")

        if not secrets.compare_digest(email, correct_email):
            flash("Unauthorized email address. Access denied.", "error")
            return render_template("login.html")

        if not secrets.compare_digest(password, correct_password):
            flash("Incorrect password. Please try again.", "error")
            return render_template("login.html")

        session.clear()
        session["librarian_logged_in"] = True
        session["librarian_email"] = email

        flash("Login successful! Welcome to Admin Portal.", "success")
        return redirect(url_for("admin"))

    return render_template("login.html")


# =====================================
# LOGOUT
# =====================================

@app.route("/logout")
@login_required
def logout():

    session.clear()
    flash("You have been logged out.", "success")

    return redirect(url_for("login"))


# =====================================
# GET LIBRARY DATA
# =====================================

def get_library_data():

    conn = get_db_connection()

    try:
        data = pd.read_sql_query("""
            SELECT
                loans.Loan_ID,
                books.Book_ID,
                books.Book_Title,
                books.Author,
                books.Category,
                books.Book_Origin,
                loans.Issue_Date,
                loans.Due_Date,
                loans.Return_Date,
                loans.Loan_Status
            FROM loans
            JOIN books ON loans.Book_ID = books.Book_ID
        """, conn)
    finally:
        conn.close()

    if data.empty:
        return data

    today = datetime.now().date()

    for column in ["Issue_Date", "Due_Date", "Return_Date"]:
        data[column] = pd.to_datetime(
            data[column], errors="coerce"
        )

    for index, row in data.iterrows():

        if row["Loan_Status"] == "Returned":
            continue

        due_date = row["Due_Date"]

        if pd.isna(due_date):
            continue

        if due_date.date() < today:
            data.at[index, "Loan_Status"] = "Overdue"
        else:
            data.at[index, "Loan_Status"] = "Active"

    return data


# =====================================
# BOOK INVENTORY DATA
# =====================================

def get_inventory_data():

    conn = get_db_connection()

    try:
        rows = conn.execute("""
            SELECT
                books.Book_Title,
                books.Author,
                books.Category,
                books.Book_Origin,

                COUNT(DISTINCT books.Book_ID) AS Total_Copies,

                COUNT(DISTINCT CASE
                    WHEN loans.Return_Date IS NULL
                    THEN books.Book_ID
                END) AS Issued_Copies

            FROM books

            LEFT JOIN loans
                ON books.Book_ID = loans.Book_ID

            GROUP BY
                books.Book_Title,
                books.Author,
                books.Category,
                books.Book_Origin

            ORDER BY books.Book_Title
        """).fetchall()

    finally:
        conn.close()

    inventory = []

    for row in rows:

        total = int(row["Total_Copies"])
        issued = int(row["Issued_Copies"])
        available = total - issued

        percentage = (
            round((available / total) * 100, 1)
            if total > 0 else 0
        )

        inventory.append({
            "Book_Title": row["Book_Title"],
            "Author": row["Author"],
            "Category": row["Category"],
            "Book_Origin": row["Book_Origin"],
            "Total_Copies": total,
            "Available_Copies": available,
            "Issued_Copies": issued,
            "Availability_Percentage": percentage
        })

    return inventory


# =====================================
# DYNAMIC CHART DATA
# =====================================

def get_chart_data():

    data = get_library_data()

    if data.empty:
        return {
            "monthly": {"labels": [], "values": []},
            "top_books": {"labels": [], "values": []},
            "categories": {"labels": [], "values": []},
            "status": {
                "labels": ["Returned", "Active", "Overdue"],
                "values": [0, 0, 0]
            }
        }

    valid_dates = data.dropna(
        subset=["Issue_Date"]
    ).copy()

    valid_dates["Month"] = (
        valid_dates["Issue_Date"].dt.to_period("M")
    )

    monthly = valid_dates.groupby("Month").size()
    top_books = data["Book_Title"].value_counts().head(10)
    categories = data["Category"].value_counts()
    statuses = data["Loan_Status"].value_counts()

    return {
        "monthly": {
            "labels": [str(x) for x in monthly.index],
            "values": [int(x) for x in monthly.values]
        },
        "top_books": {
            "labels": top_books.index.tolist(),
            "values": [int(x) for x in top_books.values]
        },
        "categories": {
            "labels": categories.index.tolist(),
            "values": [int(x) for x in categories.values]
        },
        "status": {
            "labels": ["Returned", "Active", "Overdue"],
            "values": [
                int(statuses.get("Returned", 0)),
                int(statuses.get("Active", 0)),
                int(statuses.get("Overdue", 0))
            ]
        }
    }


# =====================================
# RETURN ANALYTICS
# =====================================

def get_return_metrics(data):

    if data.empty:
        return 0, 0, 0, 0

    returned_data = data[
        data["Loan_Status"] == "Returned"
    ].copy()

    valid_returns = returned_data.dropna(
        subset=["Due_Date", "Return_Date"]
    )

    late = valid_returns[
        valid_returns["Return_Date"] > valid_returns["Due_Date"]
    ]

    valid_count = len(valid_returns)
    late_count = len(late)
    on_time_count = valid_count - late_count

    late_rate = (
        late_count / valid_count * 100
        if valid_count else 0
    )

    return (
        valid_count,
        late_count,
        on_time_count,
        round(late_rate, 2)
    )


# =====================================
# DASHBOARD
# =====================================

@app.route("/")
def index():

    data = get_library_data()

    total_borrowings = len(data)

    status_count = (
        data["Loan_Status"].value_counts()
        if not data.empty else {}
    )

    returned = int(status_count.get("Returned", 0))
    active = int(status_count.get("Active", 0))
    overdue = int(status_count.get("Overdue", 0))

    total_categories = (
        int(data["Category"].nunique())
        if not data.empty else 0
    )

    _, late_returns, _, late_rate = get_return_metrics(data)

    inventory = get_inventory_data()
    total_copies = sum(item["Total_Copies"] for item in inventory)
    available_copies = sum(item["Available_Copies"] for item in inventory)
    issued_copies = sum(item["Issued_Copies"] for item in inventory)

    chart_data = json.dumps(get_chart_data())

    return render_template(
        "index.html",
        total_books=total_copies,
        total_borrowings=total_borrowings,
        returned=returned,
        active=active,
        overdue=overdue,
        late_returns=late_returns,
        total_categories=total_categories,
        late_rate=late_rate,
        chart_data=chart_data,
        available_copies=available_copies,
        issued_copies=issued_copies
    )


# =====================================
# BOOKS PAGE
# =====================================

@app.route("/books")
def books():

    conn = get_db_connection()

    try:
        books_data = conn.execute("""
            SELECT * FROM books
            ORDER BY Book_Title
        """).fetchall()

    finally:
        conn.close()

    return render_template(
        "books.html",
        books=[dict(row) for row in books_data]
    )


# =====================================
# BOOK INVENTORY PAGE
# =====================================

@app.route("/inventory")
def inventory():

    inventory_data = get_inventory_data()

    total_titles = len(inventory_data)
    total_copies = sum(
        item["Total_Copies"] for item in inventory_data
    )
    available_copies = sum(
        item["Available_Copies"] for item in inventory_data
    )
    issued_copies = sum(
        item["Issued_Copies"] for item in inventory_data
    )

    return render_template(
        "inventory.html",
        inventory=inventory_data,
        total_titles=total_titles,
        total_copies=total_copies,
        available_copies=available_copies,
        issued_copies=issued_copies
    )


# =====================================
# CATEGORIES PAGE
# =====================================

@app.route("/categories")
def categories():

    data = get_library_data()

    if data.empty:
        categories_list = []

    else:
        category_data = data.groupby("Category").agg(
            Total_Borrowings=("Loan_ID", "count"),
            Unique_Books=("Book_ID", "nunique")
        ).reset_index()

        category_data = category_data.sort_values(
            by="Total_Borrowings",
            ascending=False
        )

        categories_list = category_data.to_dict(
            orient="records"
        )

    return render_template(
        "categories.html",
        categories=categories_list
    )


# =====================================
# CIRCULATION PAGE
# =====================================

@app.route("/circulation")
def circulation():

    data = get_library_data()

    columns = [
        "Loan_ID",
        "Book_Title",
        "Issue_Date",
        "Due_Date",
        "Return_Date",
        "Loan_Status"
    ]

    circulation_data = data[columns].copy()

    if not circulation_data.empty:

        for column in ["Issue_Date", "Due_Date"]:
            circulation_data[column] = (
                circulation_data[column].dt.strftime("%Y-%m-%d")
            )

        circulation_data["Return_Date"] = (
            circulation_data["Return_Date"].apply(
                lambda value:
                value.strftime("%Y-%m-%d")
                if pd.notna(value)
                else "Not Returned"
            )
        )

        circulation_data = circulation_data.sort_values(
            by="Issue_Date",
            ascending=False
        )

    return render_template(
        "circulation.html",
        circulation=circulation_data.to_dict(
            orient="records"
        )
    )


# =====================================
# REPORTS PAGE
# =====================================

@app.route("/reports")
def reports():

    data = get_library_data()

    total_borrowings = len(data)

    total_books = (
        int(data["Book_ID"].nunique())
        if not data.empty else 0
    )

    total_categories = (
        int(data["Category"].nunique())
        if not data.empty else 0
    )

    status_count = (
        data["Loan_Status"].value_counts()
        if not data.empty else {}
    )

    total_returned = int(status_count.get("Returned", 0))
    total_active = int(status_count.get("Active", 0))
    total_overdue = int(status_count.get("Overdue", 0))

    (
        total_valid_returns,
        total_late_returns,
        on_time_returns,
        late_return_rate
    ) = get_return_metrics(data)

    category_count = (
        data["Category"].value_counts()
        if not data.empty
        else pd.Series(dtype=int)
    )

    most_borrowed_category = (
        category_count.idxmax()
        if not category_count.empty else "N/A"
    )

    highest_category_borrowings = (
        int(category_count.max())
        if not category_count.empty else 0
    )

    book_count = (
        data["Book_Title"].value_counts()
        if not data.empty
        else pd.Series(dtype=int)
    )

    most_borrowed_book = (
        book_count.idxmax()
        if not book_count.empty else "N/A"
    )

    highest_book_borrowings = (
        int(book_count.max())
        if not book_count.empty else 0
    )

    monthly_count = pd.Series(dtype=int)

    if not data.empty:

        valid_issue_dates = data.dropna(
            subset=["Issue_Date"]
        ).copy()

        valid_issue_dates["Month"] = (
            valid_issue_dates["Issue_Date"].dt.to_period("M")
        )

        monthly_count = valid_issue_dates.groupby("Month").size()

    if not monthly_count.empty:

        busiest_month = str(monthly_count.idxmax())
        busiest_month_borrowings = int(monthly_count.max())

    else:
        busiest_month = "N/A"
        busiest_month_borrowings = 0

    missing_return_dates = (
        int(data["Return_Date"].isna().sum())
        if not data.empty else 0
    )

    chart_data = json.dumps(get_chart_data())

    return render_template(
        "reports.html",
        total_borrowings=total_borrowings,
        total_books=total_books,
        total_categories=total_categories,
        total_returned=total_returned,
        total_active=total_active,
        total_overdue=total_overdue,
        total_valid_returns=total_valid_returns,
        total_late_returns=total_late_returns,
        on_time_returns=on_time_returns,
        late_return_rate=late_return_rate,
        most_borrowed_category=most_borrowed_category,
        highest_category_borrowings=highest_category_borrowings,
        most_borrowed_book=most_borrowed_book,
        highest_book_borrowings=highest_book_borrowings,
        busiest_month=busiest_month,
        busiest_month_borrowings=busiest_month_borrowings,
        missing_return_dates=missing_return_dates,
        chart_data=chart_data
    )


# =====================================
# SMART INSIGHTS
# =====================================

@app.route("/insights")
def insights():

    data = get_library_data()
    insights_list = []

    if data.empty:

        insights_list.append(
            "Library mein abhi koi borrowing record available nahi hai."
        )

    else:

        category_counts = data["Category"].value_counts()

        if not category_counts.empty:

            popular_category = category_counts.idxmax()
            popular_count = int(category_counts.max())

            insights_list.append(
                f"{popular_category} is the most borrowed category "
                f"with {popular_count} borrowings."
            )

        book_counts = data["Book_Title"].value_counts()

        if not book_counts.empty:

            popular_book = book_counts.idxmax()
            popular_book_count = int(book_counts.max())

            insights_list.append(
                f"{popular_book} is the most borrowed book "
                f"with {popular_book_count} borrowings."
            )

        (
            valid_returns,
            late_returns,
            on_time_returns,
            late_rate
        ) = get_return_metrics(data)

        if valid_returns > 0:

            insights_list.append(
                f"Late return rate is {late_rate}% "
                f"({late_returns} late returns out of "
                f"{valid_returns} valid returned records)."
            )

            insights_list.append(
                f"{on_time_returns} books were returned on time."
            )

        else:

            insights_list.append(
                "There are not enough returned records "
                "to calculate the late return rate."
            )

        status_counts = data["Loan_Status"].value_counts()

        active_count = int(status_counts.get("Active", 0))
        overdue_count = int(status_counts.get("Overdue", 0))

        insights_list.append(
            f"There are currently {active_count} active loans "
            f"and {overdue_count} overdue loans."
        )

        monthly_data = data.dropna(
            subset=["Issue_Date"]
        ).copy()

        if not monthly_data.empty:

            monthly_data["Month"] = (
                monthly_data["Issue_Date"].dt.to_period("M")
            )

            monthly_counts = monthly_data.groupby("Month").size()

            busiest_month = str(monthly_counts.idxmax())

            insights_list.append(
                f"The busiest borrowing month is {busiest_month} "
                f"with {int(monthly_counts.max())} borrowings."
            )

    return render_template(
        "insights.html",
        insights=insights_list
    )


# =====================================
# DOWNLOAD CSV REPORT
# =====================================

@app.route("/download-report")
def download_report():

    data = get_library_data()

    report_columns = [
        "Loan_ID",
        "Book_ID",
        "Book_Title",
        "Author",
        "Category",
        "Book_Origin",
        "Issue_Date",
        "Due_Date",
        "Return_Date",
        "Loan_Status"
    ]

    report_columns = [
        column for column in report_columns
        if column in data.columns
    ]

    report_data = data[report_columns].copy()

    output = io.StringIO()

    report_data.to_csv(output, index=False)
    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=smart_library_report.csv"
        }
    )


# =====================================
# ADMIN DASHBOARD
# =====================================

@app.route("/admin")
@login_required
def admin():

    conn = get_db_connection()

    try:

        books_data = conn.execute("""
            SELECT *
            FROM books
            ORDER BY Book_Title
        """).fetchall()

        loans_data = conn.execute("""
            SELECT
                loans.Loan_ID,
                loans.Book_ID,
                books.Book_Title,
                loans.Issue_Date,
                loans.Due_Date,
                loans.Return_Date,
                loans.Loan_Status
            FROM loans
            JOIN books
            ON loans.Book_ID = books.Book_ID
            ORDER BY loans.Issue_Date DESC
            LIMIT 100
        """).fetchall()

    finally:
        conn.close()

    data = get_library_data()

    today = pd.Timestamp.today().normalize()

    due_tomorrow = []
    overdue_loans = []

    if not data.empty:

        for _, loan in data.iterrows():

            if pd.isna(loan["Due_Date"]):
                continue

            due_date = loan["Due_Date"].normalize()

            loan_info = {
                "Loan_ID": loan["Loan_ID"],
                "Book_Title": loan["Book_Title"],
                "Due_Date": due_date.strftime("%Y-%m-%d"),
                "Loan_Status": loan["Loan_Status"]
            }

            if loan["Loan_Status"] == "Overdue":
                overdue_loans.append(loan_info)

            elif (
                loan["Loan_Status"] == "Active"
                and due_date == today + pd.Timedelta(days=1)
            ):
                due_tomorrow.append(loan_info)

    return render_template(
        "admin.html",
        books=[dict(row) for row in books_data],
        loans=[dict(row) for row in loans_data],
        due_tomorrow=due_tomorrow,
        overdue_loans=overdue_loans
    )


# =====================================
# ADD NEW BOOK COPY
# =====================================

@app.route("/add-book", methods=["POST"])
@login_required
def add_book():

    book_id = request.form.get("book_id", "").strip()
    book_title = request.form.get("book_title", "").strip()
    author = request.form.get("author", "").strip()
    category = request.form.get("category", "").strip()
    book_origin = request.form.get("book_origin", "").strip()

    if not all([
        book_id,
        book_title,
        author,
        category,
        book_origin
    ]):
        flash("Please fill all book details.", "error")
        return redirect(url_for("admin"))

    conn = get_db_connection()

    try:

        conn.execute("""
            INSERT INTO books (
                Book_ID,
                Book_Title,
                Author,
                Category,
                Book_Origin
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            book_id,
            book_title,
            author,
            category,
            book_origin
        ))

        conn.commit()

        flash(
            "Book copy added successfully to inventory!",
            "success"
        )

    except sqlite3.IntegrityError:

        flash(
            "Book ID already exists. Use a unique Book ID for each copy.",
            "error"
        )

    except sqlite3.Error:

        flash("Unable to add book. Please check the details.", "error")

    finally:
        conn.close()

    return redirect(url_for("admin"))


# =====================================
# ISSUE BOOK
# =====================================

@app.route("/issue-book", methods=["POST"])
@login_required
def issue_book():

    book_id = request.form.get("book_id", "").strip()
    issue_date = request.form.get("issue_date", "").strip()
    due_date = request.form.get("due_date", "").strip()

    if not all([book_id, issue_date, due_date]):
        flash("Please fill all issue details.", "error")
        return redirect(url_for("admin"))

    try:

        issue = pd.to_datetime(issue_date, errors="raise")
        due = pd.to_datetime(due_date, errors="raise")

        if due <= issue:
            flash("Due date must be after the issue date.", "error")
            return redirect(url_for("admin"))

    except (ValueError, TypeError):

        flash("Please enter valid dates.", "error")
        return redirect(url_for("admin"))

    conn = get_db_connection()

    try:

        book = conn.execute("""
            SELECT Book_ID
            FROM books
            WHERE Book_ID = ?
        """, (book_id,)).fetchone()

        if book is None:
            flash("Book ID does not exist.", "error")
            return redirect(url_for("admin"))

        active_loan = conn.execute("""
            SELECT Loan_ID
            FROM loans
            WHERE Book_ID = ?
            AND Return_Date IS NULL
        """, (book_id,)).fetchone()

        if active_loan:
            flash(
                "This copy is already issued and not yet returned.",
                "error"
            )
            return redirect(url_for("admin"))

        # Generate a unique loan ID safely
        last_loan = conn.execute("""
            SELECT MAX(CAST(SUBSTR(Loan_ID, 2) AS INTEGER))
            FROM loans
            WHERE Loan_ID GLOB 'L[0-9]*'
        """).fetchone()[0]

        new_loan_id = f"L{(last_loan or 0) + 1:04d}"

        conn.execute("""
            INSERT INTO loans (
                Loan_ID,
                Book_ID,
                Issue_Date,
                Due_Date,
                Return_Date,
                Loan_Status
            )
            VALUES (?, ?, ?, ?, NULL, 'Active')
        """, (
            new_loan_id,
            book_id,
            issue.strftime("%Y-%m-%d"),
            due.strftime("%Y-%m-%d")
        ))

        conn.commit()

        flash(
            f"Book issued successfully! Loan ID: {new_loan_id}",
            "success"
        )

    except (sqlite3.Error, ValueError):

        flash("Unable to issue book. Please check the details.", "error")

    finally:
        conn.close()

    return redirect(url_for("admin"))


# =====================================
# RETURN BOOK
# =====================================

@app.route("/return-book", methods=["POST"])
@login_required
def return_book():

    loan_id = request.form.get("loan_id", "").strip()
    return_date = request.form.get("return_date", "").strip()

    if not loan_id or not return_date:
        flash("Please enter Loan ID and return date.", "error")
        return redirect(url_for("admin"))

    try:
        parsed_return_date = pd.to_datetime(
            return_date,
            errors="raise"
        )
    except (ValueError, TypeError):
        flash("Please enter a valid return date.", "error")
        return redirect(url_for("admin"))

    conn = get_db_connection()

    try:

        loan = conn.execute("""
            SELECT Issue_Date, Return_Date
            FROM loans
            WHERE Loan_ID = ?
        """, (loan_id,)).fetchone()

        if loan is None:
            flash("Loan ID not found.", "error")
            return redirect(url_for("admin"))

        if loan["Return_Date"] is not None:
            flash("This book has already been returned.", "error")
            return redirect(url_for("admin"))

        issue_date = pd.to_datetime(loan["Issue_Date"])

        if parsed_return_date < issue_date:
            flash(
                "Return date cannot be before issue date.",
                "error"
            )
            return redirect(url_for("admin"))

        conn.execute("""
            UPDATE loans
            SET Return_Date = ?,
                Loan_Status = 'Returned'
            WHERE Loan_ID = ?
        """, (
            parsed_return_date.strftime("%Y-%m-%d"),
            loan_id
        ))

        conn.commit()

        flash("Book returned successfully!", "success")

    except sqlite3.Error:
        flash("Unable to return book. Please try again.", "error")

    finally:
        conn.close()

    return redirect(url_for("admin"))


# =====================================
# RUN FLASK APPLICATION
# =====================================

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
