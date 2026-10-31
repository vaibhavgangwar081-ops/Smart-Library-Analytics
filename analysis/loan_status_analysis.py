#Is chart mein Returned, Active aur Overdue books ka comparison hoga.


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

# Loan status count
status_count = data["Loan_Status"].value_counts()

print("\n----- LOAN STATUS ANALYSIS -----")
print(status_count)

# Pie chart banana
plt.figure(figsize=(8, 8))

plt.pie(
    status_count,
    labels=status_count.index,
    autopct="%1.1f%%",
    startangle=90
)

plt.title("Library Loan Status Analysis")

plt.tight_layout()

# Chart save karna
image_path = report_folder / "loan_status_analysis.png"

plt.savefig(image_path, dpi=300, bbox_inches="tight")

print("\nChart saved successfully!")
print("File location:", image_path)

# Chart display karna
plt.show()
