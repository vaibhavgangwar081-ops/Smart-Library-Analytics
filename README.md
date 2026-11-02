# 📚 Smart Library Analytics System

**Turning Library Records into Useful Insights**

A simple web-based data analytics project that helps understand how books are used in a library.

---

## 💡 What is this Project?

A library has many books and borrowing records, but these records are not always easy to understand.

**Smart Library Analytics System** makes this information easier to read and analyze.

It studies library borrowing records and helps answer questions like:

- Which books are borrowed the most?
- Which book categories are most popular?
- In which month do people borrow more books?
- How many books are returned on time or late?
- How many loans are still active or overdue?

Instead of checking records one by one, users can view the results through a simple dashboard, charts, and reports.

## ✨ What Can You Do With It?

| Section | What it shows |
|---|---|
| 🏠 Dashboard | A quick overview of important library statistics |
| 📖 Books Analysis | The most borrowed books |
| 📂 Category Analysis | Borrowing records for different book categories |
| 📅 Monthly Circulation | Month-wise book borrowing trends |
| 🔄 Loan Status | Returned, active, and overdue loans |
| 📊 Reports | Important findings, statistics, and charts |

## 🔍 How Does It Work?

The project follows a simple process:

**Library Data → Python Analysis → Charts & Reports → Web Dashboard**

1. **Read the Data:** The system reads library records from a CSV file.
2. **Analyze the Data:** Python and Pandas process the records and calculate useful statistics.
3. **Create Charts:** Matplotlib creates graphs to make the results easier to understand.
4. **Show the Results:** Flask connects the analysis with the website, where users can view the information.

## 📊 What Analysis Does It Perform?

The system focuses on four main areas:

- **Book Analysis:** Finds which books have the highest number of borrowings.
- **Category Analysis:** Compares borrowing across different book categories.
- **Monthly Analysis:** Shows how borrowing activity changes over time.
- **Loan Analysis:** Checks loan status, missing return dates, and late returns.

It also calculates the late return rate using completed returns with valid due dates and return dates.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| HTML | Creates the web page structure |
| CSS | Makes the website look better |
| JavaScript | Adds basic interactions |
| Python | Handles the backend and analysis |
| Flask | Connects the Python backend to the website |
| Pandas | Reads and analyzes library data |
| Matplotlib | Creates charts and graphs |
| CSV | Stores the sample dataset |

## 📁 Project Structure

```text
SMART_LIBRARY_ANALYTICS/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Required Python libraries
│
├── dataset/
│   └── library_data.csv   # Sample library records
│
├── analysis/              # Python analysis files
│   ├── read_data.py
│   ├── monthly_analysis.py
│   ├── top_books_analysis.py
│   ├── category_analysis.py
│   └── loan_status_analysis.py
│
├── templates/             # Website pages
│   ├── index.html
│   ├── books.html
│   ├── categories.html
│   ├── circulation.html
│   └── reports.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/            # Analysis charts
│
└── reports/               # Generated analysis charts
```

## 📂 About the Dataset

This project uses a sample dataset containing **200 library borrowing records**.

The dataset includes information such as:

- Book ID
- Book Title
- Book Category
- Borrow Date
- Due Date
- Return Date
- Loan Status

The data is created for learning and project purposes. It does not contain real library member information.

## 🚀 How to Run the Project

Follow these steps to run the project on your computer.

**1. Clone the repository**

```bash
git clone https://github.com/vaibhavgangwar081-ops/Smart-Library-Analytics.git
```

**2. Open the project folder**

```bash
cd Smart-Library-Analytics
```

**3. Create a virtual environment (optional)**

```bash
python -m venv venv
```

**4. Activate the environment (Windows)**

```bash
venv\Scripts\activate
```

**5. Install the required libraries**

```bash
pip install -r requirements.txt
```

**6. Start the application**

```bash
python app.py
```

**7. Open the website**

Visit this address in your browser:

```text
http://127.0.0.1:5000
```

## 🎯 Why Did We Build This Project?

The main idea behind this project is to make library records more useful.

By understanding book demand, popular categories, monthly borrowing trends, and return patterns, library staff can get a clearer picture of library usage.

These insights can help with:

- Planning future book purchases.
- Understanding which categories need more books.
- Monitoring late returns.
- Improving library services.

## 🔮 Future Improvements

Some ideas for improving the project in the future:

- Upload new datasets directly through the website.
- Add filters for dates, books, and categories.
- Add database support.
- Improve the dashboard with more interactive charts.
- Deploy the website online.

## 📌 Project Status

The main website pages, Python analysis, charts, and reports have been created
