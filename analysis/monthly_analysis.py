
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# Project folder ka path
project_folder = Path(__file__).resolve().parent.parent

# Dataset ka path
file_path = project_folder / "dataset" / "library_data.csv"

# Reports folder ka path
report_folder = project_folder / "reports"

# Reports folder nahi hai toh create karna
report_folder.mkdir(parents=True, exist_ok=True)

# CSV read karna
data = pd.read_csv(file_path)

# Issue_Date ko datetime mein convert karna
data["Issue_Date"] = pd.to_datetime(data["Issue_Date"])

# Month-wise book issue count
data["Month"] = data["Issue_Date"].dt.to_period("M")

monthly_data = data["Month"].value_counts().sort_index()

print("\n----- MONTHLY CIRCULATION ANALYSIS -----")
print(monthly_data)

# Monthly circulation ka bar chart
plt.figure(figsize=(12, 6))

monthly_data.plot(kind="bar")

plt.title("Monthly Library Circulation")
plt.xlabel("Month")
plt.ylabel("Number of Books Issued")
plt.xticks(rotation=45)

plt.tight_layout()

# Chart ko PNG file mein save karna
image_path = report_folder / "monthly_circulation.png"

plt.savefig(image_path, dpi=300, bbox_inches="tight")

print("\nChart saved successfully!")
print("File location:", image_path)

# Chart display karna
plt.show()
