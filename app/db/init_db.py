from sqlalchemy import create_engine, text
from random import choice, randint, uniform, sample
from datetime import date, timedelta
import random
import string

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, future=True)

FIRST_NAMES = [
    "Aarav", "Vivaan", "Nishkarsh", "Vihaan", "Arjun", "Sai", "Reyansh", "Krishna",
    "Ishaan", "Shaurya", "Atharv", "Kabir", "Dhruv", "Rohan", "Kunal", "Nikhil",
    "Ananya", "Diya", "Aadhya", "Kiara", "Myra", "Anika", "Riya", "Saanvi",
    "Priya", "Meera", "Ira", "Navya", "Kavya", "Tara", "Nish", "Rahul",
    "Amit", "Komal", "Sakshi", "Pooja", "Sneha", "Aman", "Antra", "Yash",
    "Varun", "Mansi", "Isha", "Tanvi", "Palak", "Simran", "Neha", "Ritika",
    "Rijwan", "Parth", "Manav", "Laksh", "Ansh", "Ved", "Rudra", "Om"
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Patel", "Yadav", "Kumar", "Das",
    "Roy", "Mishra", "Chopra", "Jain", "Nair", "Reddy", "Joshi", "Agarwal",
    "Malhotra", "Kapoor", "Bose", "Ghosh", "Pandey", "Trivedi", "Kulkarni",
    "Menon", "Bhat", "Saxena", "Dubey", "Rastogi", "Arora", "Khanna"
]

CITIES = [
    "Delhi", "Mumbai", "Bengaluru", "Kolkata", "Pune", "Hyderabad",
    "Chennai", "Ahmedabad", "Jaipur", "Lucknow", "Jabalpur", "Bhopal",
    "Surat", "Noida", "Gurugram", "Patna", "Nagpur", "Chandigarh"
]

STATES = {
    "Delhi": "Delhi",
    "Mumbai": "Maharashtra",
    "Bengaluru": "Karnataka",
    "Kolkata": "West Bengal",
    "Pune": "Maharashtra",
    "Hyderabad": "Telangana",
    "Chennai": "Tamil Nadu",
    "Ahmedabad": "Gujarat",
    "Jaipur": "Rajasthan",
    "Lucknow": "Uttar Pradesh",
    "Jabalpur": "Madhya Pradesh",
    "Bhopal": "Madhya Pradesh",
    "Surat": "Gujarat",
    "Noida": "Uttar Pradesh",
    "Gurugram": "Haryana",
    "Patna": "Bihar",
    "Nagpur": "Maharashtra",
    "Chandigarh": "Chandigarh"
}

PRODUCTS = [
    ("Laptop", "Electronics", 55000, 95000),
    ("Phone", "Electronics", 12000, 80000),
    ("Headphones", "Electronics", 1500, 12000),
    ("Keyboard", "Electronics", 800, 6000),
    ("Mouse", "Electronics", 500, 3500),
    ("Monitor", "Electronics", 7000, 30000),
    ("Tablet", "Electronics", 10000, 50000),
    ("Smartwatch", "Electronics", 2000, 25000),
    ("Office Chair", "Furniture", 4000, 18000),
    ("Study Desk", "Furniture", 3500, 22000),
    ("Bookshelf", "Furniture", 2500, 15000),
    ("Water Bottle", "Lifestyle", 250, 1500),
    ("Backpack", "Lifestyle", 700, 5000),
    ("Yoga Mat", "Lifestyle", 600, 3500),
    ("Running Shoes", "Fashion", 1800, 12000),
    ("T-Shirt", "Fashion", 350, 2500),
    ("Jeans", "Fashion", 900, 5000),
    ("Jacket", "Fashion", 1500, 9000),
    ("Watch", "Fashion", 1200, 15000),
    ("Novel", "Books", 200, 900),
    ("Notebook", "Books", 80, 500),
    ("Pen Set", "Books", 100, 700),
    ("Data Structures Book", "Books", 350, 1500),
    ("Protein Jar", "Health", 1200, 4500),
    ("Dumbbells", "Health", 900, 6000),
    ("Face Wash", "Beauty", 180, 1200),
    ("Perfume", "Beauty", 700, 5000),
    ("Mixer Grinder", "Home Appliances", 1800, 7000),
    ("Air Fryer", "Home Appliances", 3500, 12000),
    ("Coffee Maker", "Home Appliances", 2500, 9000)
]

STATUSES = ["paid", "pending", "cancelled", "shipped", "refunded"]
PAYMENT_METHODS = ["card", "upi", "net_banking", "cash_on_delivery", "wallet"]
CHANNELS = ["web", "android_app", "ios_app"]
USER_SEGMENTS = ["student", "professional", "family", "business", "creator"]

BASE_SIGNUP_DATE = date(2024, 1, 1)
BASE_ORDER_DATE = date(2024, 6, 1)

random.seed(42)


def random_name() -> str:
    return f"{choice(FIRST_NAMES)} {choice(LAST_NAMES)}"


def random_email(name: str, user_id: int) -> str:
    clean_name = name.lower().replace(" ", ".").replace("'", "")
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
    return f"{clean_name}.{user_id}{suffix}@example.com"


def random_signup_date() -> str:
    return str(BASE_SIGNUP_DATE + timedelta(days=randint(0, 500)))


def random_order_date() -> str:
    return str(BASE_ORDER_DATE + timedelta(days=randint(0, 320)))


def generate_users(total_users: int = 80) -> list[dict]:
    users = []
    used_names = set()

    for user_id in range(1, total_users + 1):
        name = random_name()

        # reduce duplicate full names
        attempts = 0
        while name in used_names and attempts < 20:
            name = random_name()
            attempts += 1
        used_names.add(name)

        city = choice(CITIES)
        state = STATES[city]
        segment = choice(USER_SEGMENTS)
        signup_date = random_signup_date()
        email = random_email(name, user_id)

        users.append({
            "id": user_id,
            "name": name,
            "email": email,
            "city": city,
            "state": state,
            "segment": segment,
            "signup_date": signup_date
        })

    return users


def generate_orders(users: list[dict], total_orders: int = 220) -> list[dict]:
    orders = []

    # ensure some repeat customers
    repeat_user_ids = sample([u["id"] for u in users], 20)

    for order_id in range(1, total_orders + 1):
        if order_id <= 60:
            user_id = choice(repeat_user_ids)
        else:
            user_id = choice(users)["id"]

        product_name, category, min_price, max_price = choice(PRODUCTS)
        quantity = randint(1, 5)
        unit_price = round(uniform(min_price, max_price), 2)
        amount = round(unit_price * quantity, 2)

        status = choice(STATUSES)
        payment_method = choice(PAYMENT_METHODS)
        channel = choice(CHANNELS)
        order_date = random_order_date()

        orders.append({
            "id": order_id,
            "user_id": user_id,
            "product_name": product_name,
            "category": category,
            "unit_price": unit_price,
            "quantity": quantity,
            "amount": amount,
            "status": status,
            "payment_method": payment_method,
            "channel": channel,
            "order_date": order_date
        })

    return orders


def init_db():
    users = generate_users(80)
    orders = generate_orders(users, 220)

    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS orders"))
        conn.execute(text("DROP TABLE IF EXISTS users"))

        conn.execute(text("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                segment TEXT NOT NULL,
                signup_date TEXT NOT NULL
            )
        """))

        conn.execute(text("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                category TEXT NOT NULL,
                unit_price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                channel TEXT NOT NULL,
                order_date TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """))

        for user in users:
            conn.execute(
                text("""
                    INSERT INTO users (
                        id, name, email, city, state, segment, signup_date
                    ) VALUES (
                        :id, :name, :email, :city, :state, :segment, :signup_date
                    )
                """),
                user
            )

        for order in orders:
            conn.execute(
                text("""
                    INSERT INTO orders (
                        id, user_id, product_name, category, unit_price,
                        quantity, amount, status, payment_method, channel, order_date
                    ) VALUES (
                        :id, :user_id, :product_name, :category, :unit_price,
                        :quantity, :amount, :status, :payment_method, :channel, :order_date
                    )
                """),
                order
            )

    print("Database recreated successfully.")
    print(f"Inserted {len(users)} users.")
    print(f"Inserted {len(orders)} orders.")
    print("File: test.db")


if __name__ == "__main__":
    init_db()