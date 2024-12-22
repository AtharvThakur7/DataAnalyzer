# Data Analyzer: CSV Processing and Visualization

Welcome to the Data Analyzer! This project provides a simple yet powerful interface for uploading, analyzing, and visualizing CSV data. Built with Python, Django, Pandas, Matplotlib, and Seaborn, this tool is perfect for exploring datasets interactively on the web.

![image alt ](https://github.com/AtharvThakur7/DataAnalyzer/blob/662ffadf7dc7f0c4868b288c695b1720fb523c84/Screenshot%202024-12-22%20093037.png)

## Motivation

In today’s data-driven world, making sense of raw data is a crucial skill. This project is designed to simplify the process of uploading, analyzing, and visualizing CSV data through a user-friendly web interface. Whether you're a beginner exploring data or an expert seeking quick insights, this tool empowers you with seamless analysis and visualizations.


## Installation

Clone the Repository

```bash
  https://github.com/AtharvThakur7/DataAnalyzer.git
  cd DataAnalyzer
```
Install Dependencies

```bash
  pip install django pandas matplotlib seaborn
```
Run the Server
```bash
  python manage.py runserver
```
Access the Application
```bash
  http://127.0.0.1:8000/
```

## Features

#### File Upload
Upload CSV files directly via a web form.
Files are temporarily stored for analysis.

#### Data Analysis
View the first few rows of your dataset.
Generate key summary statistics, including:
Mean
Median
Standard Deviation
Automatically identify and handle missing values.

![image alt](https://github.com/AtharvThakur7/DataAnalyzer/blob/e4df6b1e59dcd87bb284c5be26e3abe158ec0e36/Screenshot%202024-12-22%20093119.png)

#### Data Visualization
Generate and Download beautiful and informative plots, such as histograms.
Plots are created using Matplotlib and Seaborn for high-quality visuals.

![image alt](https://github.com/AtharvThakur7/DataAnalyzer/blob/b16b57951bd887533d44037a7f2f11a2be55aec2/Screenshot%202024-12-22%20093148.png)

#### Data Storage
Stores the Users Input csv or excel files in Sqlite3 Database .
![image alt]()



## Brief Explanation With Project Flow Structure

The Data Analyzer is a web-based application designed to streamline the analysis and visualization of data stored in CSV and Excel files. Built using Django as the backend framework, the application offers a seamless user experience for uploading data files, performing quick exploratory data analysis (EDA), and generating insightful visualizations.

With just a few clicks, users can:

- Upload CSV or Excel files via a user-friendly interface.
- View essential statistical summaries, such as mean, median, and standard deviation.
- Identify missing values in the dataset.
- Generate high-quality visualizations like histograms, powered by Matplotlib and Seaborn.

The project bridges the gap between raw data and actionable insights, making it an essential tool for data enthusiasts, analysts, and developers who need rapid insights from their datasets.


![image alt](https://github.com/AtharvThakur7/DataAnalyzer/blob/dc7c2b5424163175824bf7381cc85bcd13ce0706/Screenshot%202024-12-22%20102308.png)








