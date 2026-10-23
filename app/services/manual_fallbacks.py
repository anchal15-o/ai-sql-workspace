from typing import Optional


def get_manual_sql_fallback(prompt: str) -> Optional[str]:
    p = prompt.lower().strip()

    fallback_rules = [
        # BASIC
        (["show all users", "list all users"], "SELECT * FROM users LIMIT 10;"),
        (["show all orders", "list all orders"], "SELECT * FROM orders LIMIT 10;"),
        (["show user names", "list user names"], "SELECT name FROM users LIMIT 10;"),
        (["show user emails", "list user emails"], "SELECT email FROM users LIMIT 10;"),
        (["show all cities", "list all cities"], "SELECT DISTINCT city FROM users;"),
        (["show all categories", "list all categories"], "SELECT DISTINCT category FROM orders;"),
        (["show all payment methods", "list payment methods"], "SELECT DISTINCT payment_method FROM orders;"),
        (["show all order statuses", "list order statuses"], "SELECT DISTINCT status FROM orders;"),

        # FILTERS
        (["show users from delhi"], "SELECT * FROM users WHERE city = 'Delhi' LIMIT 10;"),
        (["show users from mumbai"], "SELECT * FROM users WHERE city = 'Mumbai' LIMIT 10;"),
        (["show paid orders"], "SELECT * FROM orders WHERE status = 'paid' LIMIT 10;"),
        (["show pending orders"], "SELECT * FROM orders WHERE status = 'pending' LIMIT 10;"),
        (["show cancelled orders"], "SELECT * FROM orders WHERE status = 'cancelled' LIMIT 10;"),
        (["show refunded orders"], "SELECT * FROM orders WHERE status = 'refunded' LIMIT 10;"),
        (["show orders from android app"], "SELECT * FROM orders WHERE channel = 'android_app' LIMIT 10;"),
        (["show orders from ios app"], "SELECT * FROM orders WHERE channel = 'ios_app' LIMIT 10;"),
        (["show orders from web"], "SELECT * FROM orders WHERE channel = 'web' LIMIT 10;"),
        (["show orders with amount greater than 5000", "show orders above 5000"], "SELECT * FROM orders WHERE amount > 5000 ORDER BY amount DESC LIMIT 10;"),
        (["show orders with amount less than 1000", "show orders below 1000"], "SELECT * FROM orders WHERE amount < 1000 ORDER BY amount ASC LIMIT 10;"),

        # SORTING
        (["show top 10 highest value orders", "show highest value orders"], "SELECT * FROM orders ORDER BY amount DESC LIMIT 10;"),
        (["show lowest value orders"], "SELECT * FROM orders ORDER BY amount ASC LIMIT 10;"),
        (["show latest orders"], "SELECT * FROM orders ORDER BY order_date DESC LIMIT 10;"),
        (["show oldest orders"], "SELECT * FROM orders ORDER BY order_date ASC LIMIT 10;"),
        (["show users sorted by signup date"], "SELECT * FROM users ORDER BY signup_date DESC LIMIT 10;"),

        # COUNTS
        (["total number of users", "count users"], "SELECT COUNT(*) AS total_users FROM users;"),
        (["total number of orders", "count orders"], "SELECT COUNT(*) AS total_orders FROM orders;"),
        (["show number of users by segment"], "SELECT segment, COUNT(*) AS user_count FROM users GROUP BY segment ORDER BY user_count DESC LIMIT 10;"),
        (["count orders by status"], "SELECT status, COUNT(*) AS order_count FROM orders GROUP BY status ORDER BY order_count DESC LIMIT 10;"),
        (["count orders by payment method"], "SELECT payment_method, COUNT(*) AS order_count FROM orders GROUP BY payment_method ORDER BY order_count DESC LIMIT 10;"),
        (["count orders by channel"], "SELECT channel, COUNT(*) AS order_count FROM orders GROUP BY channel ORDER BY order_count DESC LIMIT 10;"),

        # AGGREGATIONS
        (["show total sales by category"], "SELECT category, SUM(amount) AS total_sales FROM orders GROUP BY category ORDER BY total_sales DESC LIMIT 10;"),
        (["show total sales by payment method"], "SELECT payment_method, SUM(amount) AS total_sales FROM orders GROUP BY payment_method ORDER BY total_sales DESC LIMIT 10;"),
        (["show total sales by channel"], "SELECT channel, SUM(amount) AS total_sales FROM orders GROUP BY channel ORDER BY total_sales DESC LIMIT 10;"),
        (["show average order amount by payment method", "average order amount by payment method"], "SELECT payment_method, AVG(amount) AS avg_order_amount FROM orders GROUP BY payment_method ORDER BY avg_order_amount DESC LIMIT 10;"),
        (["show average order amount by category"], "SELECT category, AVG(amount) AS avg_order_amount FROM orders GROUP BY category ORDER BY avg_order_amount DESC LIMIT 10;"),
        (["show total quantity sold by category"], "SELECT category, SUM(quantity) AS total_quantity FROM orders GROUP BY category ORDER BY total_quantity DESC LIMIT 10;"),
        (["show top categories by sales"], "SELECT category, SUM(amount) AS total_sales FROM orders GROUP BY category ORDER BY total_sales DESC LIMIT 10;"),

        # JOINS
        (["show users with their orders"], "SELECT u.id, u.name, u.city, o.id AS order_id, o.product_name, o.amount, o.status FROM users u JOIN orders o ON u.id = o.user_id LIMIT 10;"),
        (["show user name and order amount"], "SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id LIMIT 10;"),
        (["show user city and order amount"], "SELECT u.city, o.amount FROM users u JOIN orders o ON u.id = o.user_id LIMIT 10;"),
        (["show users who have orders"], "SELECT DISTINCT u.id, u.name, u.email FROM users u JOIN orders o ON u.id = o.user_id LIMIT 10;"),

        # CUSTOMER ANALYSIS
        (["top 10 users by total spending", "top users by total spending"], """
            SELECT u.id, u.name, u.city, SUM(o.amount) AS total_spending
            FROM users u
            JOIN orders o ON u.id = o.user_id
            GROUP BY u.id, u.name, u.city
            ORDER BY total_spending DESC
            LIMIT 10;
        """),
        (["top 5 users by total spending"], """
            SELECT u.id, u.name, u.city, SUM(o.amount) AS total_spending
            FROM users u
            JOIN orders o ON u.id = o.user_id
            GROUP BY u.id, u.name, u.city
            ORDER BY total_spending DESC
            LIMIT 5;
        """),
        (["show repeat customers"], """
            SELECT u.id, u.name, COUNT(o.id) AS order_count
            FROM users u
            JOIN orders o ON u.id = o.user_id
            GROUP BY u.id, u.name
            HAVING COUNT(o.id) > 1
            ORDER BY order_count DESC
            LIMIT 10;
        """),
        (["show users with no orders"], """
            SELECT u.id, u.name, u.email
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            WHERE o.id IS NULL
            LIMIT 10;
        """),
        (["show sales by city"], """
            SELECT u.city, SUM(o.amount) AS total_sales
            FROM users u
            JOIN orders o ON u.id = o.user_id
            GROUP BY u.city
            ORDER BY total_sales DESC
            LIMIT 10;
        """),
        (["show sales by segment"], """
            SELECT u.segment, SUM(o.amount) AS total_sales
            FROM users u
            JOIN orders o ON u.id = o.user_id
            GROUP BY u.segment
            ORDER BY total_sales DESC
            LIMIT 10;
        """),
        (["show total spending by city"], """
            SELECT u.city, SUM(o.amount) AS total_spending
            FROM users u
            JOIN orders o ON u.id = o.user_id
            GROUP BY u.city
            ORDER BY total_spending DESC
            LIMIT 10;
        """),

        # DATE-BASED
        (["show monthly sales"], """
            SELECT substr(order_date, 1, 7) AS month, SUM(amount) AS total_sales
            FROM orders
            GROUP BY substr(order_date, 1, 7)
            ORDER BY month
            LIMIT 12;
        """),
        (["show monthly order count"], """
            SELECT substr(order_date, 1, 7) AS month, COUNT(*) AS order_count
            FROM orders
            GROUP BY substr(order_date, 1, 7)
            ORDER BY month
            LIMIT 12;
        """),
        (["show users signed up by month"], """
            SELECT substr(signup_date, 1, 7) AS month, COUNT(*) AS user_count
            FROM users
            GROUP BY substr(signup_date, 1, 7)
            ORDER BY month
            LIMIT 12;
        """),

        # PRODUCT ANALYSIS
        (["show top products by sales"], """
            SELECT product_name, SUM(amount) AS total_sales
            FROM orders
            GROUP BY product_name
            ORDER BY total_sales DESC
            LIMIT 10;
        """),
        (["show top products by quantity"], """
            SELECT product_name, SUM(quantity) AS total_quantity
            FROM orders
            GROUP BY product_name
            ORDER BY total_quantity DESC
            LIMIT 10;
        """),
    ]

    for patterns, sql in fallback_rules:
        if any(pattern in p for pattern in patterns):
            return " ".join(sql.split())

    return None