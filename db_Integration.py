from flask import Flask, render_template, g
import sqlite3
import pandas as pd

app = Flask(__name__)

DATABASE = 'database.db'
PRODUCTS_CSV = 'Essential_Info.csv'
REVIEWS_CSV = 'reviews.csv'


@app.route('/')
def index():
    return render_template('index.html')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def create_tables():
    with app.app_context():
        db = get_db()
        # Create Products table
        db.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                UID INTEGER PRIMARY KEY,
                Name TEXT,
                Brand TEXT,
                Price REAL,
                URL TEXT,
                Rating REAL,
                Questions_Count	INTEGER,
                SKU TEXT,
                Protection TEXT,
                Year INTEGER,
                Number_Of_Cameras INTEGER
            )
        ''')
        
        # Create Reviews table
        db.execute('''
            CREATE TABLE IF NOT EXISTS Reviews (
                UID INTEGER PRIMARY KEY,
                Review_ID INTEGER,
                Name TEXT,
                Rating REAL,
                Text TEXT
            )
        ''')

        # Insert data from CSV into Products table
        products_df = pd.read_csv(PRODUCTS_CSV)
        products_df.to_sql('Products', db, if_exists='replace', index=False)

        # Insert data from CSV into Reviews table
        reviews_df = pd.read_csv(REVIEWS_CSV)
        reviews_df.to_sql('Reviews', db, if_exists='replace', index=False)

        db.commit()


@app.route('/view_products')
def view_products():
    with app.app_context():
        db = get_db()
        products_df = pd.read_sql_query('SELECT * FROM Products', db)
    return render_template('view_data.html', title='Products', data=products_df)


@app.route('/view_reviews')
def view_reviews():
    with app.app_context():
        db = get_db()
        reviews_df = pd.read_sql_query('SELECT * FROM Reviews', db)
    return render_template('view_data.html', title='Reviews', data=reviews_df)


if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
