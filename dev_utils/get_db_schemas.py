import sqlite3
from pathlib import Path

# Paths to the databases
db_default_path = Path(__file__).resolve().parents[1] / "db_app.sqlite3"
db_images_path = Path(__file__).resolve().parents[1] / "db_images.sqlite3"


def get_db_schemas(db_path):
    """
    Connect to the SQLite database and retrieve the schema definitions.
    """

    # Prevent SQLite from creating new database if path is invalid
    if not db_path.exists():
        print(f"Error: Database does not exist at {db_path}")
        return

    try:
        # Connect to the SQLite database
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Query the sqlite_master table to retrieve schema definitions
        cursor.execute(
            "SELECT name, type, sql FROM sqlite_master WHERE type IN ('table', 'index', 'view');"
        )
        schemas = cursor.fetchall()

        # Print the results
        print(f"\nSchema for database: {db_path}")
        if not schemas:
            print("No tables, indexes, or views found.")
        for name, obj_type, sql in schemas:
            print(f"  {obj_type.upper()}: {name}")
            print(f"    Definition: {sql}")
            print("-" * 70)

    except sqlite3.Error as e:
        print(f"Error accessing database {db_path}: {e}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    print("Inspecting database schemas...\n")

    # Check the default database
    get_db_schemas(db_default_path)

    # Check the images database
    get_db_schemas(db_images_path)
