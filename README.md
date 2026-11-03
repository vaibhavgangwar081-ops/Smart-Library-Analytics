# 📚 D-016 Smart Library Analytics System

**Turning Library Records into Useful Insights**

## 💡 Project Overview

Smart Library Analytics is a web-based data analytics project that helps libraries understand book borrowing patterns and monitor book circulation.

It analyzes library records and displays useful information through an interactive dashboard, charts, reports and smart insights.

## ✨ Key Features

| Section | What it shows |
|---|---|
| Dashboard | Overview of library statistics |
| Books Analysis | Most borrowed books |
| Category Analysis | Popular book categories |
| Monthly Circulation | Month-wise borrowing trends |
| Loan Status | Returned, active and overdue loans |
| Reports | Analytics, statistics and charts |
| Smart Insights | Data-based recommendations |
| CSV Download | Downloadable analytics report |

## 🔍 How Does It Work?

**Library Data → Python Analysis → Charts & Reports → Web Dashboard**

1. Read library records from a CSV file.
2. Analyze data using Python and Pandas.
3. Generate charts using Matplotlib.
4. Display results through a Flask website.

## 📊 Analysis Performed

- Most borrowed books
- Category-wise borrowing
- Monthly circulation trends
- Returned, active and overdue loans
- Missing return dates
- Late return rate

Late return rate is calculated using completed returns with valid due dates and return dates.

## 🛠️ Technologies Used

- Python
- Flask
- Pandas
- NumPy
- HTML
- CSS
- JavaScript
- Matplotlib
- CSV Dataset

## 📂 Dataset

The project uses a synthetic dataset containing 200 library loan records.

It includes:
- Loan ID
- Book ID and title
- Author and category
- Book origin
- Issue date
- Due date
- Return date
- Loan status

The dataset is created for academic purposes and does not contain real library member information.

## 📁 Project Structure

```text
SMART_LIBRARY_ANALYTICS/
├── app.py
├── requirements.txt
├── README.md
├── analysis/
├── dataset/
├── reports/
├── templates/
│   ├── index.html
│   ├── books.html
│   ├── categories.html
│   ├── circulation.html
│   ├── reports.html
│   └── insights.html
└── static/
    ├── css/
    ├── js/
    └── images/
```

## 🚀 How to Run the Project

1. Clone the repository:

```bash
git clone https://github.com/vaibhavgangwar081-ops/Smart-Library-Analytics.git
```

2. Open the project folder:

```bash
cd Smart-Library-Analytics/SMART_LIBRARY_ANALYTICS
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the Flask application:

```bash
python app.py
```

5. Open this address in your browser:

```text
http://127.0.0.1:5000
```

## 🎯 Project Purpose

The system helps libraries understand borrowing trends, identify popular books and categories, monitor late returns and make informed collection-planning decisions.

## 🔮 Future Improvements

- Upload datasets directly through the website.
- Add database support.
- Add more interactive charts.
- Deploy the website online.

## 📌 Project Status

The main website pages, Python analysis scripts, charts, reports and Smart Insights feature have been developed.

**Note:** This project uses synthetic sample data for academic purposes.