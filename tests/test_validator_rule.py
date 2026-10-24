"""test"""

import json
from src.db.database import get_connection
extensions = [".pdf", ".png", ".xyz"]

try:
    with get_connection() as connection:
        result = connection.execute("""
            SELECT DISTINCT r.id, r.category, j.value AS extension
            FROM rules AS r,
                json_each(r.value) AS j
            WHERE r.type = 'extension'
            AND j.value IN (
            SELECT value
            FROM json_each(?)
            )
        """, (json.dumps(extensions),))

        rows = result.fetchall()

        if rows:
            for row in rows:
                print(
                    f"Rule ID: {row[0]} | "
                    f"Category: {row[1]} | "
                    f"Extension: {row[2]}"
                )
        else:
            print("No matching extensions found.")

except Exception as error:
    print(f"Error: {error}")
