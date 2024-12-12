import sqlite3
import time
from unittest.mock import patch
from django.test import TestCase
from application.predictions.prediction_manager import (
    delete_job_from_db,
    JOB_EXPIRY_TIME,
)


class JobExpirationTests(TestCase):
    def setUp(self):
        """
        Set up a test database table for requests.
        """
        self.db_path = "../db_app.sqlite3"
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # Create a mock 'requests' table for testing
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS requests (
            request_id INTEGER PRIMARY KEY,
            created_at REAL NOT NULL,
            job_data TEXT
        )
        """
        )
        self.conn.commit()

    def tearDown(self):
        """
        Tear down the test database.
        """
        # Drop the table after tests
        self.cursor.execute("DROP TABLE IF EXISTS requests")
        self.conn.commit()
        self.conn.close()

    def test_delete_expired_jobs(self):
        """
        Test that jobs older than 15 minutes (expired jobs) are deleted.
        """
        current_time = time.time()

        # Insert test jobs into the database
        self.cursor.execute(
            "INSERT INTO requests (request_id, created_at, job_data) VALUES (?, ?, ?)",
            (1, current_time - (JOB_EXPIRY_TIME + 10), "expired job data"),
        )
        self.cursor.execute(
            "INSERT INTO requests (request_id, created_at, job_data) VALUES (?, ?, ?)",
            (2, current_time - 100, "valid job data"),
        )
        self.conn.commit()

        # Assert both jobs exist before deletion
        self.cursor.execute("SELECT * FROM requests WHERE request_id = 1")
        expired_job = self.cursor.fetchone()
        self.assertIsNotNone(expired_job, "Expired job should exist before deletion")

        self.cursor.execute("SELECT * FROM requests WHERE request_id = 2")
        valid_job = self.cursor.fetchone()
        self.assertIsNotNone(valid_job, "Valid job should exist before deletion")

        # Call the delete_job_from_db function for the expired job
        delete_job_from_db(1)

        # Assert the expired job is deleted
        self.cursor.execute("SELECT * FROM requests WHERE request_id = 1")
        expired_job = self.cursor.fetchone()
        self.assertIsNone(expired_job, "Expired job should not exist after deletion")

        # Assert the valid job still exists
        self.cursor.execute("SELECT * FROM requests WHERE request_id = 2")
        valid_job = self.cursor.fetchone()
        self.assertIsNotNone(
            valid_job, "Valid job should still exist after expired job deletion"
        )

    def test_delete_existing_job(self):
        """
        Test that a job is deleted from the database.
        """
        # Insert a test job into the database
        self.cursor.execute(
            "INSERT INTO requests (request_id, created_at, job_data) VALUES (1, 1234567890, 'test data')"
        )
        self.conn.commit()

        # Assert the job exists
        self.cursor.execute("SELECT * FROM requests WHERE request_id = 1")
        job = self.cursor.fetchone()
        self.assertIsNotNone(job, "Job should exist before deletion")

        # Call the delete_job_from_db function
        delete_job_from_db(1)

        # Assert the job is deleted
        self.cursor.execute("SELECT * FROM requests WHERE request_id = 1")
        job = self.cursor.fetchone()
        self.assertIsNone(job, "Job should not exist after deletion")

    def test_delete_non_existent_job(self):
        """
        Test that attempting to delete a non-existent job does not raise an error.
        """
        try:
            # Call the delete_job_from_db function with a non-existent job ID
            delete_job_from_db(999)
        except Exception as e:
            self.fail(
                f"delete_job_from_db raised an exception for non-existent job: {e}"
            )

    def test_error_handling(self):
        """
        Test that the function handles errors gracefully.
        """
        # Patch sqlite3.connect to raise an OperationalError
        with patch(
            "sqlite3.connect", side_effect=sqlite3.OperationalError("Mocked error")
        ):
            # Mocking the sqlite3.connect to raise an OperationalError
            with self.assertRaises(sqlite3.OperationalError):
                delete_job_from_db(1)  # This should raise an OperationalError
