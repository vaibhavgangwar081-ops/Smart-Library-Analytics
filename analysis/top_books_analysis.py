
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Project folder ka path
project_folder = Path(__file__).resolve().parent.parent

# Dataset aur reports folder ka path
file_path = project_folder / "dataset" / "library_data.csv"
report_folder = project_folder / "reports"

# Reports folder create karna agar nahi hai
report_folder.mkdir(parents=True, exist_ok=True)

# CSV file read karna
data = pd.read_csv(file_path)

# Top 10 most borrowed books
top_books = data["Book_Title"].value_counts().head(10)

print("\n----- TOP 10 MOST BORROWED BOOKS -----")
print(top_books)

# Bar chart banana
plt.figure(figsize=(12, 7))

top_books.sort_values().plot(kind="barh")

plt.title("Top 10 Most Borrowed Books")
plt.xlabel("Number of Times Borrowed")
plt.ylabel("Book Title")

plt.tight_layout()

# Chart save karna
image_path = report_folder / "top_10_books.png"
plt.savefig(image_path, dpi=300, bbox_inches="tight")

print("\nChart saved successfully!")
print("File location:", image_path)

# Chart display karna
plt.show()
