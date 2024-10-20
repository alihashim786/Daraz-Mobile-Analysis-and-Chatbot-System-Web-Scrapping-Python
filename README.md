# Daraz-Mobile-Analysis-and-Chatbot-System-Web-Scrapping-Python
An advanced system for analyzing mobile products from Daraz.pk using web scraping, data analysis, and an interactive chatbot powered by natural language processing. It features a dashboard for visual insights and uses Flask for web integration.


# Daraz Mobile Analysis and Chatbot System

This project is an advanced mobile product analysis and chatbot system developed by scraping data from Daraz.pk. The system extracts data, stores it in a structured format, and provides interactive chatbot functionality for user queries. Additionally, a dashboard provides insights into mobile product trends, prices, and reviews.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [Contributing](#contributing)

## Features
- **Web Scraping**: Automated scraping of mobile product data from Daraz.pk using BeautifulSoup.
- **Data Storage**: Scraped data is stored in CSV files and SQLite database for easy access and analysis.
- **Interactive Chatbot**: A natural language chatbot developed to answer queries like "What is the best phone under $300?"
- **Dashboard**: A Flask-powered dashboard that visualizes the scraped data, including top-rated products, average prices, and more.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/Daraz-Mobile-Analysis-Chatbot.git
    ```
2. Install the required Python libraries:
    ```bash
    pip install -r requirements.txt
    ```
3. Start the Flask app:
    ```bash
    python app.py
    ```
4. Open your browser and navigate to:
    ```
    http://127.0.0.1:5000
    ```

## Usage

1. **Scraping Data**: 
    - Run the scraping script to gather mobile product data from Daraz.pk:
      ```bash
      jupyter notebook i220554_scraping.ipynb
      ```
2. **Interactive Chatbot**: 
    - Ask questions about mobile products, like "Show me phones under Rs. 50,000" or "Which phone has the best rating?"
3. **Dashboard**: 
    - Access the dashboard via Flask to view data trends, top-rated products, and price distributions.

## Architecture

- **Web Scraping**: Collects data on mobile products (name, price, reviews) from Daraz.pk.
- **Data Storage**: Data is stored in CSV files (`ALL_DATA.csv`, `reviews.csv`, etc.) and an SQLite database (`database.db`).
- **Chatbot**: Uses NLP techniques to answer user queries based on the data.
- **Flask Dashboard**: Provides visual insights into product trends and reviews.

### Files Overview
- `app.py`: Main Flask application script.
- `db_Integration.py`: Handles database integration for storing and retrieving scraped data.
- `i220554_scraping.ipynb`: Jupyter notebook containing the web scraping logic.
- `ALL_DATA.csv`, `reviews.csv`, `Specifications.csv`: CSV files storing scraped mobile data.


## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.
