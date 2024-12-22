# Data Analyzer: CSV Processing and Visualization

Welcome to the Django CSV Processor and Visualizer! This project provides a simple yet powerful interface for uploading, analyzing, and visualizing CSV data. Built with Python, Django, Pandas, Matplotlib, and Seaborn, this tool is perfect for exploring datasets interactively on the web.

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

### File Upload
Upload CSV files directly via a web form.
Files are temporarily stored for analysis.

### Data Analysis
View the first few rows of your dataset.
Generate key summary statistics, including:
Mean
Median
Standard Deviation
Automatically identify and handle missing values.

![image alt](https://github.com/AtharvThakur7/DataAnalyzer/blob/e4df6b1e59dcd87bb284c5be26e3abe158ec0e36/Screenshot%202024-12-22%20093119.png)

### Data Visualization
Generate beautiful and informative plots, such as histograms.
Plots are created using Matplotlib and Seaborn for high-quality visuals.


![image alt](https://github.com/AtharvThakur7/DataAnalyzer/blob/b16b57951bd887533d44037a7f2f11a2be55aec2/Screenshot%202024-12-22%20093148.png)






