def looks_like_date_column(name: str) -> bool:
    key = name.lower()
    return any(word in key for word in ["date", "month", "time", "year"])


def looks_like_dimension_column(name: str) -> bool:
    key = name.lower()
    return any(
        word in key
        for word in [
            "city",
            "state",
            "segment",
            "status",
            "category",
            "payment",
            "channel",
            "name",
            "month",
            "product",
        ]
    )


def suggest_chart(result: dict) -> dict:
    columns = result.get("columns", [])
    rows = result.get("rows", [])

    if not rows or len(columns) < 2:
        return {
            "type": "none",
            "title": "No chart available",
            "reason": "Not enough structured data for charting."
        }

    numeric_columns = []
    text_columns = []

    for col in columns:
        has_numeric = any(isinstance(row.get(col), (int, float)) for row in rows)
        if has_numeric:
            numeric_columns.append(col)
        else:
            text_columns.append(col)

    metric = None
    for col in numeric_columns:
        if any(word in col.lower() for word in ["total", "count", "avg", "amount", "sales", "spending", "quantity", "value", "revenue"]):
            metric = col
            break
    if metric is None and numeric_columns:
        metric = numeric_columns[0]

    dimension = None
    for col in text_columns:
        if looks_like_date_column(col):
            dimension = col
            break
    if dimension is None:
        for col in text_columns:
            if looks_like_dimension_column(col):
                dimension = col
                break
    if dimension is None and text_columns:
        dimension = text_columns[0]

    if not metric or not dimension:
        return {
            "type": "none",
            "title": "No chart available",
            "reason": "Could not find a clear metric and dimension."
        }

    if looks_like_date_column(dimension):
        return {
            "type": "line",
            "title": f"{metric} over {dimension}",
            "reason": "Time-like data is best shown as a trend.",
            "x_axis": dimension,
            "y_axis": metric
        }

    if len(rows) <= 6:
        return {
            "type": "pie",
            "title": f"{metric} by {dimension}",
            "reason": "A small grouped distribution works well as a pie chart.",
            "label_key": dimension,
            "value_key": metric
        }

    return {
        "type": "bar",
        "title": f"{metric} by {dimension}",
        "reason": "Grouped comparisons are easiest to read as bars.",
        "x_axis": dimension,
        "y_axis": metric
    }