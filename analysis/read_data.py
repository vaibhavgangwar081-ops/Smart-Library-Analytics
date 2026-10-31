
import pandas as pd
from pathlib import Path

# Project ke dataset folder ka path
project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "dataset" / "library_data.csv"

# CSV file read karna
data = pd.read_csv(file_path)

# Convert date columns into datetime format
date_columns = ["Issue_Date", "Due_Date", "Return_Date"]

for column in date_columns:
    data[column] = pd.to_datetime(data[column], errors="coerce")

print("\n----- DATE DATA TYPES -----")
print(data[date_columns].dtypes)

# Check missing values
print("\n----- MISSING VALUES -----")
print(data.isnull().sum())

# Check loan status
print("\n----- LOAN STATUS COUNT -----")
print(data["Loan_Status"].value_counts())

# Late return analysis
returned_books = data[data["Loan_Status"] == "Returned"].copy()

returned_books["Late_Days"] = (
    returned_books["Return_Date"] - returned_books["Due_Date"]
).dt.days

late_books = returned_books[returned_books["Late_Days"] > 0]

on_time_books = returned_books[returned_books["Late_Days"] <= 0]

late_return_rate = (len(late_books) / len(returned_books)) * 100

print("\n----- LATE RETURN ANALYSIS -----")
print("Total Returned Books:", len(returned_books))
print("Late Returned Books:", len(late_books))
print("On-Time Returned Books:", len(on_time_books))
print("Late Return Rate:", round(late_return_rate, 2), "%")

# Most borrowed books analysis
print("\n----- TOP 10 MOST BORROWED BOOKS -----")

top_books = data["Book_Title"].value_counts().head(10)

print(top_books)

# Category-wise borrowing analysis
print("\n----- CATEGORY-WISE BORROWING -----")

category_count = data["Category"].value_counts()

print(category_count)

print("\nMost Borrowed Category:")
print(category_count.idxmax())

# First 5 records show karna
print("\n----- FIRST 5 RECORDS -----")
print(data.head().to_string())

# Total rows and columns
print("\n----- DATASET SHAPE -----")
print(data.shape)

# Column names
print("\n----- COLUMN NAMES -----")
print(data.columns.tolist())

# Dataset information
print("\n----- DATASET INFORMATION -----")
data.info()
