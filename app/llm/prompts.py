def build_sql_prompt(user_prompt: str, schema_info: list[dict], dialect: str = "sqlite") -> str:
    schema_lines = []

    for table in schema_info:
        table_name = table["table_name"]
        cols = ", ".join(col["name"] for col in table["columns"])
        schema_lines.append(f"{table_name}({cols})")

    schema_text = "\n".join(schema_lines)

    return f"""
Return exactly one valid {dialect} SQL query.

Database schema:
{schema_text}

Rules:
- Output only SQL
- No explanation
- No markdown
- Only SELECT
- Use only tables and columns from the schema
- Use SQLite syntax
- Use LIMIT not TOP
- If using aggregate functions, include proper GROUP BY
- For "top users by total spending", join users and orders using users.id = orders.user_id
- For "sales by category", use SUM(amount) grouped by category
- For "average order amount by payment method", use AVG(amount) grouped by payment_method
- For "number of users by segment", use COUNT(*) grouped by segment
- For "repeat customers", return users with COUNT(orders.id) > 1
- Always include LIMIT 10 unless a different limit is requested

Examples:
SELECT * FROM users LIMIT 10;

SELECT category, SUM(amount) AS total_sales
FROM orders
GROUP BY category
ORDER BY total_sales DESC
LIMIT 10;

SELECT payment_method, AVG(amount) AS avg_order_amount
FROM orders
GROUP BY payment_method
ORDER BY avg_order_amount DESC
LIMIT 10;

SELECT u.id, u.name, COUNT(o.id) AS order_count
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name
HAVING COUNT(o.id) > 1
ORDER BY order_count DESC
LIMIT 10;

User request:
{user_prompt}
""".strip()