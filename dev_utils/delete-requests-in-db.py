import sqlite3

# Path to SQLite database file
db_path = "../db_app.sqlite3"

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Step 1: Check if there are any records in the Requests table
    cursor.execute("SELECT COUNT(*) FROM requests;")
    record_count = cursor.fetchone()[0]

    if record_count > 0:
        print(f"There are {record_count} records in the 'requests' table.")

        # Step 2: Delete all records from the Requests table
        cursor.execute("DELETE FROM requests;")
        conn.commit()
        print("All records have been deleted from the 'requests' table.")
    else:
        print("No records found in the 'requests' table.")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    # Close the connection to the database
    cursor.close()
    conn.close()
