from flask import Flask, render_template, make_response
import pandas as pd
from pathlib import Path

app = Flask(__name__)

# Project folder path
BASE_DIR = Path(__file__).resolve().parent

# Dataset path
data_path = BASE_DIR / "dataset" / "library_data.csv"


# =====================================
# DASHBOARD PAGE
# =====================================

@app.route("/")
def index():

    data = pd.read_csv(data_path)

    # Total borrowing records
    total_books = len(data)

    # Loan status count
    status_count = data["Loan_Status"].value_counts()

    returned = int(status_count.get("Returned", 0))
    active = int(status_count.get("Active", 0))
    overdue = int(status_count.get("Overdue", 0))

    # Total unique categories
    total_categories = data["Category"].nunique()

    # Late return analysis
    returned_data = data[
        data["Loan_Status"] == "Returned"
    ].copy()

    returned_data["Due_Date"] = pd.to_datetime(
        returned_data["Due_Date"], errors="coerce"
    )

    returned_data["Return_Date"] = pd.to_datetime(
        returned_data["Return_Date"], errors="coerce"
    )

    valid_returns = returned_data.dropna(
        subset=["Due_Date", "Return_Date"]
    )

    late_books = valid_returns[
        valid_returns["Return_Date"] > valid_returns["Due_Date"]
    ]

    late_returns = len(late_books)

    late_rate = (
        (late_returns / len(valid_returns)) * 100
        if len(valid_returns) > 0 else 0
    )

    return render_template(
        "index.html",
        total_books=total_books,
        returned=returned,
        active=active,
        overdue=overdue,
        late_returns=late_returns,
        total_categories=total_categories,
        late_rate=round(late_rate, 2)
    )


# =====================================
# BOOKS PAGE
# =====================================

@app.route("/books")
def books():

    data = pd.read_csv(data_path)

    books_data = data[
        [
            "Book_ID",
            "Book_Title",
            "Author",
            "Category",
            "Book_Origin"
        ]
    ].drop_duplicates(subset=["Book_ID"])

    books_list = books_data.to_dict(orient="records")

    return render_template(
        "books.html",
        books=books_list
    )


# =====================================
# CATEGORIES PAGE
# =====================================

@app.route("/categories")
def categories():

    data = pd.read_csv(data_path)

    category_data = data.groupby("Category").agg(
        Total_Borrowings=("Loan_ID", "count"),
        Unique_Books=("Book_ID", "nunique")
    ).reset_index()

    category_data = category_data.sort_values(
        by="Total_Borrowings",
        ascending=False
    )

    categories_list = category_data.to_dict(orient="records")

    return render_template(
        "categories.html",
        categories=categories_list
    )


# =====================================
# CIRCULATION PAGE
# =====================================

@app.route("/circulation")
def circulation():

    data = pd.read_csv(data_path)

    circulation_data = data[
        [
            "Loan_ID",
            "Book_Title",
            "Issue_Date",
            "Due_Date",
            "Return_Date",
            "Loan_Status"
        ]
    ].copy()

    circulation_data["Return_Date"] = (
        circulation_data["Return_Date"].fillna("Not Returned")
    )

    circulation_data = circulation_data.sort_values(
        by="Issue_Date",
        ascending=False
    )

    circulation_list = circulation_data.to_dict(
        orient="records"
    )

    return render_template(
        "circulation.html",
        circulation=circulation_list
    )


# =====================================
# REPORTS PAGE
# =====================================

@app.route("/reports")
def reports():

    data = pd.read_csv(data_path)

    # Basic summary
    total_borrowings = len(data)
    total_books = data["Book_ID"].nunique()
    total_categories = data["Category"].nunique()

    # Loan status summary
    status_count = data["Loan_Status"].value_counts()

    total_returned = int(status_count.get("Returned", 0))
    total_active = int(status_count.get("Active", 0))
    total_overdue = int(status_count.get("Overdue", 0))

    # Convert date columns
    data["Due_Date"] = pd.to_datetime(
        data["Due_Date"], errors="coerce"
    )

    data["Return_Date"] = pd.to_datetime(
        data["Return_Date"], errors="coerce"
    )

    # Only completed returned records with valid dates
    valid_returns = data[
        (data["Loan_Status"] == "Returned") &
        data["Due_Date"].notna() &
        data["Return_Date"].notna()
    ].copy()

    # Late return records
    late_books = valid_returns[
        valid_returns["Return_Date"] > valid_returns["Due_Date"]
    ]

    total_valid_returns = len(valid_returns)
    total_late_returns = len(late_books)

    # Late return percentage
    late_return_rate = (
        (total_late_returns / total_valid_returns) * 100
        if total_valid_returns > 0 else 0
    )

    # On-time returned books
    on_time_returns = total_valid_returns - total_late_returns

    # Category-wise analysis
    category_count = data["Category"].value_counts()

    most_borrowed_category = (
        category_count.idxmax()
        if not category_count.empty else "N/A"
    )

    highest_category_borrowings = (
        int(category_count.max())
        if not category_count.empty else 0
    )

    # Most borrowed book
    book_count = data["Book_Title"].value_counts()

    most_borrowed_book = (
        book_count.idxmax()
        if not book_count.empty else "N/A"
    )

    highest_book_borrowings = (
        int(book_count.max())
        if not book_count.empty else 0
    )

    # Monthly circulation analysis
    data["Issue_Date"] = pd.to_datetime(
        data["Issue_Date"], errors="coerce"
    )

    valid_issue_dates = data.dropna(subset=["Issue_Date"]).copy()

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

    # Missing return date count
    missing_return_dates = int(data["Return_Date"].isna().sum())

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
        late_return_rate=round(late_return_rate, 2),
        most_borrowed_category=most_borrowed_category,
        highest_category_borrowings=highest_category_borrowings,
        most_borrowed_book=most_borrowed_book,
        highest_book_borrowings=highest_book_borrowings,
        busiest_month=busiest_month,
        busiest_month_borrowings=busiest_month_borrowings,
        missing_return_dates=missing_return_dates
    )

# =====================================
# SMART LIBRARY INSIGHTS
# =====================================

@app.route("/insights")
def insights():

    data = pd.read_csv(data_path)

    insights_list = []

    # 1. Most popular category
    category_count = data["Category"].value_counts()

    if not category_count.empty:
        popular_category = category_count.idxmax()
        popular_count = int(category_count.max())

        insights_list.append({
            "title": "Most Popular Category",
            "value": popular_category,
            "description": (
                f"{popular_category} has the highest borrowing "
                f"with {popular_count} recorded loans."
            )
        })

    # 2. Most borrowed book
    book_count = data["Book_Title"].value_counts()

    if not book_count.empty:
        popular_book = book_count.idxmax()
        book_loans = int(book_count.max())

        insights_list.append({
            "title": "Most Borrowed Book",
            "value": popular_book,
            "description": (
                f"This book has been borrowed {book_loans} times."
            )
        })

    # 3. Late return analysis
    data["Due_Date"] = pd.to_datetime(
        data["Due_Date"], errors="coerce"
    )

    data["Return_Date"] = pd.to_datetime(
        data["Return_Date"], errors="coerce"
    )

    valid_returns = data[
        (data["Loan_Status"] == "Returned") &
        data["Due_Date"].notna() &
        data["Return_Date"].notna()
    ]

    late_returns = valid_returns[
        valid_returns["Return_Date"] > valid_returns["Due_Date"]
    ]

    late_rate = (
        len(late_returns) / len(valid_returns) * 100
        if len(valid_returns) > 0 else 0
    )

    insights_list.append({
        "title": "Late Return Rate",
        "value": f"{late_rate:.1f}%",
        "description": (
            "Monitor return reminders and due-date awareness "
            "to improve timely book returns."
        )
    })

    # 4. Library collection suggestion
    if not category_count.empty:
        insights_list.append({
            "title": "Collection Planning",
            "value": popular_category,
            "description": (
                f"Consider reviewing the availability of "
                f"{popular_category} books because this category "
                f"has the highest borrowing demand."
            )
        })

    return render_template(
        "insights.html",
        insights=insights_list
    )

# =====================================
# DOWNLOAD ANALYTICS REPORT
# =====================================

@app.route("/download-report")
def download_report():

    data = pd.read_csv(data_path)

    # Basic statistics
    total_borrowings = len(data)
    total_books = data["Book_ID"].nunique()
    total_categories = data["Category"].nunique()

    status_count = data["Loan_Status"].value_counts()

    total_returned = int(status_count.get("Returned", 0))
    total_active = int(status_count.get("Active", 0))
    total_overdue = int(status_count.get("Overdue", 0))

    # Late return analysis
    data["Due_Date"] = pd.to_datetime(
        data["Due_Date"], errors="coerce"
    )
    data["Return_Date"] = pd.to_datetime(
        data["Return_Date"], errors="coerce"
    )

    valid_returns = data[
        (data["Loan_Status"] == "Returned") &
        data["Due_Date"].notna() &
        data["Return_Date"].notna()
    ]

    late_returns = valid_returns[
        valid_returns["Return_Date"] > valid_returns["Due_Date"]
    ]

    total_valid_returns = len(valid_returns)
    total_late_returns = len(late_returns)

    late_rate = (
        (total_late_returns / total_valid_returns) * 100
        if total_valid_returns > 0 else 0
    )

    # Create summary report
    report_data = {
        "Metric": [
            "Total Borrowings",
            "Unique Books",
            "Total Categories",
            "Returned Loans",
            "Active Loans",
            "Overdue Loans",
            "Valid Returned Records",
            "Late Returns",
            "On-Time Returns",
            "Late Return Rate (%)"
        ],
        "Value": [
            total_borrowings,
            total_books,
            total_categories,
            total_returned,
            total_active,
            total_overdue,
            total_valid_returns,
            total_late_returns,
            total_valid_returns - total_late_returns,
            round(late_rate, 2)
        ]
    }

    report_df = pd.DataFrame(report_data)

    # Create downloadable CSV response
    response = make_response(report_df.to_csv(index=False))

    response.headers["Content-Disposition"] = (
        "attachment; filename=library_analytics_report.csv"
    )
    response.headers["Content-Type"] = "text/csv; charset=utf-8"

    return response


# =====================================
# RUN FLASK APPLICATION
# =====================================

if __name__ == "__main__":
    app.run(debug=True)
