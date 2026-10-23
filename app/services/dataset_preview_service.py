from sqlalchemy import text

import re
def get_dataset_preview(engine) -> dict:
    with engine.connect() as conn:
        total_users = conn.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0
        total_orders = conn.execute(text("SELECT COUNT(*) FROM orders")).scalar() or 0
        distinct_categories = conn.execute(text("SELECT COUNT(DISTINCT category) FROM orders")).scalar() or 0
        distinct_cities = conn.execute(text("SELECT COUNT(DISTINCT city) FROM users")).scalar() or 0

        users_result = conn.execute(
            text("""
                SELECT id, name, email, city, state, segment, signup_date
                FROM users
                ORDER BY id
                LIMIT 5
            """)
        )
        users_rows = [dict(row._mapping) for row in users_result]

        orders_result = conn.execute(
            text("""
                SELECT id, user_id, product_name, category, unit_price, quantity, amount, status, payment_method, channel, order_date
                FROM orders
                ORDER BY id
                LIMIT 5
            """)
        )
        orders_rows = [dict(row._mapping) for row in orders_result]

    return {
        "ok": True,
        "stats": {
            "total_users": total_users,
            "total_orders": total_orders,
            "distinct_categories": distinct_categories,
            "distinct_cities": distinct_cities,
        },
        "tables": [
            {
                "table_name": "users",
                "columns": ["id", "name", "email", "city", "state", "segment", "signup_date"],
                "sample_rows": users_rows,
            },
            {
                "table_name": "orders",
                "columns": ["id", "user_id", "product_name", "category", "unit_price", "quantity", "amount", "status", "payment_method", "channel", "order_date"],
                "sample_rows": orders_rows,
            },
        ],
    }