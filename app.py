from flask import Flask, render_template, request, g, session
import nltk
from flask_session import Session
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
nltk.download('punkt')
import sqlite3

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Additional function to get statistics about products
def get_product_statistics():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

# Calculate total number of listings
        total_listings_query = "SELECT COUNT(DISTINCT UID) FROM Products"
        total_listings = cursor.execute(total_listings_query).fetchone()[0]

# Calculate average product price
        avg_price_query = "SELECT AVG(Price) FROM Products"
        avg_price = cursor.execute(avg_price_query).fetchone()[0]

# Calculate average ratings of products
        avg_rating_query = "SELECT AVG(Rating) FROM Products"
        avg_rating = cursor.execute(avg_rating_query).fetchone()[0]

# Calculate average review count per product
        avg_review_count_query = """
            SELECT AVG(user_avg) 
            FROM (
                SELECT UID, AVG(Rating) AS user_avg 
                FROM Reviews 
                GROUP BY UID
            ) AS user_avgs
        """
        cursor.execute(avg_review_count_query)
        avg_review_count = cursor.fetchone()[0]

# Calculate total number of questions asked
        total_questions_asked_query = "SELECT IFNULL(SUM(Questions_Count), 0) FROM Products"
        total_questions_asked = cursor.execute(
            total_questions_asked_query).fetchone()[0]

# Retrieve top 5 products based on highest ratings
        top_rated_products_query = "SELECT * FROM Products ORDER BY Rating DESC LIMIT 5"
        top_rated_products = cursor.execute(
            top_rated_products_query).fetchall()

        return {
            'total_listings': total_listings,
            'avg_price': avg_price,
            'avg_rating': avg_rating,
            'avg_review_count': avg_review_count,
            'top_rated_products': top_rated_products,
            'total_questions_asked': total_questions_asked
        }


# preprocess the query using NLTK
def preprocess_query(query):
    words = word_tokenize(query)
    return words

# get the database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
    return db

def get_available_brands():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

# unique brands from the 'Brand' column in the 'Products' table
        unique_brands_query = "SELECT DISTINCT LOWER(Brand) FROM Products"
        cursor.execute(unique_brands_query)
        unique_brands = [row[0] for row in cursor.fetchall()]

    return unique_brands

def chatbot(query):
    query_words = preprocess_query(query)
# Greetings
    if any(greeting in query_words for greeting in ["hello", "hi", "hey", "how are you"]):
        response = "Hello! How can I assist you today?"

# Price and Rating
    elif any(word.isdigit() or (word[:-1].isdigit() and word[-1] == 'k') for word in query_words) and 'rating' in query_words:
        numbers = []

        min_rating = None
        target_price = None
        over_price = False
        below_price = False
        between_price = False

# Find numbers(price and rating) from the query 
        for i, word in enumerate(query_words):
            try:
                num = float(word)
                if num <= 5:
                    min_rating = num
            except ValueError:
                pass

            if word.isdigit():
                numbers.append(int(word))
            elif word[:-1].isdigit() and word[-1] == 'k':
                numbers.append(int(word[:-1]) * 1000)

            if word.lower() == 'under' or word.lower() == 'below':
                below_price = True

            elif word.lower() == 'above' or word.lower() == 'over':
                over_price = True

            elif word.lower() == 'between':
                between_price = True

        if numbers:
            target_price = max(numbers)
            min_price = min(numbers)

        with app.app_context():
            db = get_db()
            cursor = db.cursor()

# check for over, below and between
            if over_price and target_price is not None and min_rating is not None:
                price_rating_query = """
                    SELECT * FROM Products 
                    WHERE Price > ? AND Rating >= ? 
                    ORDER BY Rating DESC 
                    LIMIT 5
                """
                cursor.execute(price_rating_query, (target_price, min_rating))
                products = cursor.fetchall()

            elif below_price and target_price is not None and min_rating is not None:
                price_rating_query = """
                    SELECT * FROM Products 
                    WHERE Price < ? AND Rating >= ? 
                    ORDER BY Rating DESC 
                    LIMIT 5
                """
                cursor.execute(price_rating_query, (target_price, min_rating))
                products = cursor.fetchall()

            elif between_price and target_price is not None and min_rating is not None:
                price_rating_query = """
                    SELECT * FROM Products 
                    WHERE Price BETWEEN ? AND ? AND Rating >= ? 
                    ORDER BY Rating DESC 
                    LIMIT 5
                """
                cursor.execute(price_rating_query, (min_price, target_price, min_rating))
                products = cursor.fetchall()

        if products:
            response = f"Sure! Showing products based on your criteria.<br><br>"
            response += "Top rated products:<br><br>"
            for product in products:
                product_info = f" {product[1]} - Rating: {product[4]} - Price: {product[3]} <br><a href='{product[6]}' target='_blank'>View Product</a>"
                response += f"{product_info}<br><br>"
        else:
            response = f"No products found based on your criteria."

# Price and Brand
    elif any(word.isdigit() or (word[:-1].isdigit() and word[-1] == 'k') for word in query_words) and any(brand in query_words for brand in get_available_brands()):
        numbers = []
        under_price = False
        above_price = False
        between_price = False

# Find numbers(price) from the query 
        for i, word in enumerate(query_words):
            if word.isdigit():
                numbers.append(int(word))
            elif word[:-1].isdigit() and word[-1] == 'k':
                numbers.append(int(word[:-1]) * 1000)

            if word.lower() == 'under' or word.lower() == 'below':
                under_price = True

            elif word.lower() == 'above' or word.lower() == 'over':
                above_price = True

            elif word.lower() == 'between':
                between_price = True

        if numbers:
            target_price = max(numbers)
            min_price = min(numbers)

        brand_products = []

        with app.app_context():
            db = get_db()
            cursor = db.cursor()

# Extract the brand name from the query
            brand_name = next(brand for brand in get_available_brands() if brand in query_words)

# check for over, below and between
            if under_price and numbers:
                under_price_query = """
                    SELECT * FROM Products 
                    WHERE LOWER(Brand) = LOWER(?) AND Price < ? 
                    ORDER BY Rating DESC 
                    LIMIT 5
                """
                cursor.execute(under_price_query, (brand_name, target_price))
                brand_products = cursor.fetchall()

            elif above_price and numbers:
                above_price_query = """
                    SELECT * FROM Products 
                    WHERE LOWER(Brand) = LOWER(?) AND Price > ? 
                    ORDER BY Rating DESC 
                    LIMIT 5
                """
                cursor.execute(above_price_query, (brand_name, target_price))
                brand_products = cursor.fetchall()

            elif between_price and len(numbers) == 2:
                # Fetch products within the specified price range for the brand
                between_price_query = """
                    SELECT * FROM Products 
                    WHERE LOWER(Brand) = LOWER(?) AND Price BETWEEN ? AND ? 
                    ORDER BY Rating DESC 
                    LIMIT 5
                """
                cursor.execute(between_price_query, (brand_name, min_price, target_price))
                brand_products = cursor.fetchall()

        if brand_products:
            response = f"Sure! Showing products for {brand_name}"

            if under_price and numbers:
                response += f" under {target_price}"

            elif above_price and numbers:
                response += f" above {target_price}"

            elif between_price and len(numbers) == 2:
                response += f" between {min_price} and {target_price}"

            response += " within the specified price range.<br><br>"
            response += "Top products for this brand:<br><br>"
            for product in brand_products:
                product_info = f" {product[1]} - Rating: {product[4]} - Price: {product[3]} <br><a href='{product[6]}' target='_blank'>View Product</a>"
                response += f"{product_info}<br><br>"
        else:
            response = f"No products found for {brand_name} within the specified price range."
          
# Price Only
    elif any(word.isdigit() or (word[:-1].isdigit() and word[-1] == 'k') for word in query_words):
        products_in_range = None
        products_under_price = None
        products_over_price = None

        numbers = []
# Find numbers(price) from the query 
        for word in query_words:
            if word.isdigit():
                numbers.append(int(word))
            elif word[:-1].isdigit() and word[-1] == 'k':
                numbers.append(int(word[:-1]) * 1000)

# in case of 2 numbers (price range)
        if len(numbers) == 2:
            min_price, max_price = min(numbers), max(numbers)

            with app.app_context():
                db = get_db()
                cursor = db.cursor()

                price_range_query = """
                    SELECT * FROM Products 
                    WHERE Price BETWEEN ? AND ? 
                    ORDER BY Rating DESC 
                    LIMIT 3
                """
                cursor.execute(price_range_query, (min_price, max_price))
                products_in_range = cursor.fetchall()

            if products_in_range:
                response = f"Sure! Showing products between {min_price} and {max_price}.<br><br>"
                response += "Top products in this range:<br><br>"
                for product in products_in_range:
                    product_info = f" {product[1]} - Rating: {product[4]} - Price: {product[3]} <br><a href='{product[6]}' target='_blank'>View Product</a>"
                    response += f"{product_info}<br><br>"
            else:
                response = f"No products found between {min_price} and {max_price}."

# in case of 1 number (upper/lower limit)
        elif len(numbers) == 1:
            target_price = numbers[0]

            with app.app_context():
                db = get_db()
                cursor = db.cursor()

                # Check for "under" or "below" in the query
                if any(word in query_words for word in ["under", "below"]):
                    under_price_query = """
                        SELECT * FROM Products 
                        WHERE Price < ? 
                        ORDER BY Rating DESC 
                        LIMIT 3
                    """
                    cursor.execute(under_price_query, (target_price,))
                    products_under_price = cursor.fetchall()

                    if products_under_price:
                        response = f"Sure! Showing products under {target_price}.<br><br>"
                        response += "Top products under this price:<br><br>"
                        for product in products_under_price:
                            product_info = f" {product[1]} - Rating: {product[4]} - Price: {product[3]} <br><a href='{product[6]}' target='_blank'>View Product</a>"
                            response += f"{product_info}<br><br>"
                    else:
                        response = f"No products found under {target_price}."

                # Check for "over" or "above" in the query
                elif any(word in query_words for word in ["over", "above"]):
                    over_price_query = """
                        SELECT * FROM Products 
                        WHERE Price > ? 
                        ORDER BY Rating DESC 
                        LIMIT 3
                    """
                    cursor.execute(over_price_query, (target_price,))
                    products_over_price = cursor.fetchall()

                    if products_over_price:
                        response = f"Sure! Showing products over {target_price}.<br><br>"
                        response += "Top products over this price:<br><br>"
                        for product in products_over_price:
                            product_info = f" {product[1]} - Rating: {product[4]} - Price: {product[3]} <br><a href='{product[6]}' target='_blank'>View Product</a>"
                            response += f"{product_info}<br><br>"
                    else:
                        response = f"No products found over {target_price}."

                else:
                    response = f"I'm sorry, I couldn't understand whether you are looking for products under or over {target_price}. Please specify 'under' or 'over' in your query."

        else:
            response = "I'm sorry, I couldn't understand the price range you provided. Please try again."

    return response


@app.route('/', methods=['GET', 'POST'])
def chatbot_route():
    if request.method == 'POST':
        user_query = request.form['query']
        response = chatbot(user_query)

# conversation history
        conversation = session.get('conversation', [])
        conversation.append({'query': user_query, 'response': response})
        session['conversation'] = conversation
        
# clear chat history
    elif request.method == 'GET' and request.args.get('clear_chat'):
        session.pop('conversation', None)

    conversation = session.get('conversation', [])

# Get product statistics for the dashboard
    product_statistics = get_product_statistics()

    return render_template('chatbot_dashboard.html', conversation=conversation, product_statistics=product_statistics)


if __name__ == '__main__':
    app.run(debug=True)
