# Data Analyzer: CSV Processing and Visualization

Welcome to the Data Analyzer! This project provides a simple yet powerful interface for uploading, analyzing, and visualizing CSV data. Built with Python, Django, Pandas, Matplotlib, and Seaborn, this tool is perfect for exploring datasets interactively on the web.

![image alt ](https://github.com/AtharvThakur7/DataAnalyzer/blob/662ffadf7dc7f0c4868b288c695b1720fb523c84/Screenshot%202024-12-22%20093037.png)

## Motivation

In today’s data-driven world, making sense of raw data is a crucial skill. This project is designed to simplify the process of uploading, analyzing, and visualizing CSV data through a user-friendly web interface. Whether you're a beginner exploring data or an expert seeking quick insights, this tool empowers you with seamless analysis and visualizations.


## Installation

Clone the Repository

```bash
  git clone https://github.com/AtharvThakur7/DataAnalyzer.git
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


![image alt](https://github.com/AtharvThakur7/DataAnalyzer/blob/6deea771b377ebe4732d8ca0153c44b062025107/Screenshot%202024-12-22%20102400.png)



## Brief Explanation With Project Flow Structure

The Data Analyzer is a web-based application designed to streamline the analysis and visualization of data stored in CSV and Excel files. Built using Django as the backend framework, the application offers a seamless user experience for uploading data files, performing quick exploratory data analysis (EDA), and generating insightful visualizations.

With just a few clicks, users can:

- Upload CSV or Excel files via a user-friendly interface.
- View essential statistical summaries, such as mean, median, and standard deviation.
- Identify missing values in the dataset.
- Generate high-quality visualizations like histograms, powered by Matplotlib and Seaborn.

The project bridges the gap between raw data and actionable insights, making it an essential tool for data enthusiasts, analysts, and developers who need rapid insights from their datasets.


![image alt](https://github.com/AtharvThakur7/DataAnalyzer/blob/dc7c2b5424163175824bf7381cc85bcd13ce0706/Screenshot%202024-12-22%20102308.png)



## Development Challenges


During the deployment of my Django application on Render, the deployment process completed successfully, and the application was live. However, I encountered a port binding issue that prevented the application from listening on the correct port. The application functioned correctly in the local development environment but failed to start properly in global deployment.


Despite implementing the recommended solutions, the port binding issue persists, and the application remains inaccessible externally. I would greatly appreciate any assistance to resolve this problem, ensuring the application functions end-to-end as intended.

![image alt](https://github.com/AtharvThakur7/DataAnalyzer/blob/50e15a21d0379efe0cf8e54f7eb258c1eb2a17fb/Screenshot%202024-12-22%20224256.png)




## Tech Stack

**Backend:** Django,Python

**Data Analysis:** Pandas

**Data Visualization:** Matplotlib, Seaborn

**Database:** SQLite3

**Frontend:** Django Templates (HTML, CSS)



## Future Enhancements

While the current version of the Data Analyzer provides essential tools for data analysis and visualization, future versions aim to elevate the experience by:

- Enabling end-to-end dynamic analysis and visualization, where users can filter, transform, and customize their data directly on the platform.

- Creating a dashboard view to display multiple insights simultaneously for comprehensive analysis.


## Conclusion

The Data Analyzer is more than just a tool—it's your first step toward unlocking the full potential of your data. By simplifying the process of analysis and visualization, this project empowers users to extract meaningful insights from raw data efficiently and intuitively.

We believe in continuous improvement and welcome suggestions, feedback, and contributions to make this tool even better.








