
import pandas as pd
from pathlib import Path

# Get project folder path
project_folder = Path(__file__).resolve().parent.parent

# Get dataset path
file_path = project_folder / "dataset" / "library_data.csv"

# Read CSV file
data = pd.read_csv(file_path)

print("\n========== SMART LIBRARY ANALYTICS ==========")

# ---------------------------------
# 1. DATE VALIDATION
# ---------------------------------

date_columns = ["Issue_Date", "Due_Date", "Return_Date"]

for column in date_columns:
    data[column] = pd.to_datetime(
        data[column], errors="coerce"
    )

print("\n----- DATE DATA TYPES -----")
print(data[date_columns].dtypes)

# ---------------------------------
# 2. MISSING VALUE ANALYSIS
# ---------------------------------

print("\n----- MISSING VALUES -----")
print(data.isnull().sum())

print("\nMissing Return Dates:",
      data["Return_Date"].isnull().sum())

# ---------------------------------
# 3. LOAN STATUS ANALYSIS
# ---------------------------------

print("\n----- LOAN STATUS COUNT -----")

status_count = data["Loan_Status"].value_counts()

print(status_count)

# ---------------------------------
# 4. LATE RETURN ANALYSIS
# ---------------------------------

returned_books = data[
    data["Loan_Status"] == "Returned"
].copy()

# Keep only records with valid due and return dates
valid_returns = returned_books.dropna(
    subset=["Due_Date", "Return_Date"]
).copy()

# Calculate late days
valid_returns["Late_Days"] = (
    valid_returns["Return_Date"] -
    valid_returns["Due_Date"]
).dt.days

# Separate late and on-time returns
late_books = valid_returns[
    valid_returns["Late_Days"] > 0
]

on_time_books = valid_returns[
    valid_returns["Late_Days"] <= 0
]

total_valid_returns = len(valid_returns)
total_late_returns = len(late_books)
total_on_time_returns = len(on_time_books)

# Calculate accurate late return rate
late_return_rate = (
    (total_late_returns / total_valid_returns) * 100
    if total_valid_returns > 0 else 0
)

print("\n----- LATE RETURN ANALYSIS -----")

print("Total Returned Records:",
      len(returned_books))

print("Valid Returned Records:",
      total_valid_returns)

print("Late Returned Books:",
      total_late_returns)

print("On-Time Returned Books:",
      total_on_time_returns)

print("Returned Records with Missing Dates:",
      len(returned_books) - total_valid_returns)

print("Late Return Rate:",
      round(late_return_rate, 2), "%")

# ---------------------------------
# 5. TOP 10 MOST BORROWED BOOKS
# ---------------------------------

print("\n----- TOP 10 MOST BORROWED BOOKS -----")

top_books = data["Book_Title"].value_counts().head(10)

print(top_books)

# ---------------------------------
# 6. CATEGORY-WISE ANALYSIS
# ---------------------------------

print("\n----- CATEGORY-WISE BORROWING -----")

category_count = data["Category"].value_counts()

print(category_count)

if not category_count.empty:
    print("\nMost Borrowed Category:",
          category_count.idxmax())

# ---------------------------------
# 7. MONTHLY CIRCULATION ANALYSIS
# ---------------------------------

print("\n----- MONTHLY CIRCULATION -----")

valid_issue_dates = data.dropna(
    subset=["Issue_Date"]
).copy()

valid_issue_dates["Month"] = (
    valid_issue_dates["Issue_Date"].dt.to_period("M")
)

monthly_count = (
    valid_issue_dates.groupby("Month").size()
)

print(monthly_count)

if not monthly_count.empty:
    print("\nBusiest Month:", monthly_count.idxmax())
    print("Total Borrowings:",
          monthly_count.max())

# ---------------------------------
# 8. DATASET INFORMATION
# ---------------------------------

print("\n----- FIRST 5 RECORDS -----")
print(data.head().to_string())

print("\n----- DATASET SHAPE -----")
print(data.shape)

print("\n----- COLUMN NAMES -----")
print(data.columns.tolist())

print("\n----- DATASET INFORMATION -----")
data.info()


# ---------------------------------
# 9. DATA QUALITY VALIDATION
# ---------------------------------

print("\n----- DATA QUALITY VALIDATION -----")

# Check duplicate Loan IDs
duplicate_loans = data["Loan_ID"].duplicated().sum()

print("Duplicate Loan IDs:", duplicate_loans)

# Check duplicate Book IDs in catalogue
# Repeated Book IDs in borrowing records are normal.
book_catalogue = data[
    ["Book_ID", "Book_Title", "Author", "Category"]
].drop_duplicates()

inconsistent_books = (
    book_catalogue.groupby("Book_ID")[
        ["Book_Title", "Author", "Category"]
    ].nunique().gt(1).any(axis=1).sum()
)

print("Inconsistent Book Records:", inconsistent_books)

# Check invalid date order
invalid_due_dates = (
    data["Due_Date"] < data["Issue_Date"]
).sum()

invalid_return_dates = (
    data["Return_Date"].notna() &
    (data["Return_Date"] < data["Issue_Date"])
).sum()

print("Due Dates Before Issue Dates:", invalid_due_dates)
print("Return Dates Before Issue Dates:", invalid_return_dates)

# Check loan status consistency
invalid_returned = (
    (data["Loan_Status"] == "Returned") &
    data["Return_Date"].isna()
).sum()

invalid_unreturned = (
    (data["Loan_Status"].isin(["Active", "Overdue"])) &
    data["Return_Date"].notna()
).sum()

print("Returned Loans Without Return Date:", invalid_returned)
print("Active/Overdue Loans With Return Date:", invalid_unreturned)

# Final validation result
total_errors = (
    duplicate_loans +
    inconsistent_books +
    invalid_due_dates +
    invalid_return_dates +
    invalid_returned +
    invalid_unreturned
)

print("\nTotal Validation Errors:", total_errors)

if total_errors == 0:
    print("Data Quality Status: PASSED")
else:
    print("Data Quality Status: NEEDS REVIEW")


print("\n========== ANALYSIS COMPLETED ==========")

