#Is chart se pata chalega ki library mein Fiction, Fantasy, History aur doosri categories mein se kis category ki books sabse zyada borrow hui hain.


import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Project folder ka path
project_folder = Path(__file__).resolve().parent.parent

# Dataset aur reports folder
file_path = project_folder / "dataset" / "library_data.csv"
report_folder = project_folder / "reports"

# Reports folder create karna
report_folder.mkdir(parents=True, exist_ok=True)

# CSV read karna
data = pd.read_csv(file_path)

# Category-wise book count
category_count = data["Category"].value_counts()

print("\n----- CATEGORY-WISE BORROWING -----")
print(category_count)

print("\nMost Borrowed Category:")
print(category_count.idxmax())

# Bar chart banana
plt.figure(figsize=(12, 7))

category_count.sort_values().plot(kind="barh")

plt.title("Category-wise Library Borrowing")
plt.xlabel("Number of Books Borrowed")
plt.ylabel("Book Category")

plt.tight_layout()

# Chart save karna
image_path = report_folder / "category_analysis.png"

plt.savefig(image_path, dpi=300, bbox_inches="tight")

print("\nChart saved successfully!")
print("File location:", image_path)

# Chart display karna
plt.show()
