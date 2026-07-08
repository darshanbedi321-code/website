import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self):
        self.conn = None
        self.mycursor = None
        self.connection_error = None
        try:
            self.conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                dbname=os.getenv("DB_NAME"),
                port=int(os.getenv("DB_PORT")),
                connect_timeout=10
            )
            self.mycursor = self.conn.cursor()
        except Exception as e:
            self.connection_error = str(e)
            print("Connection Error:", e)

    def store(self, name):
        if self.conn is None or self.mycursor is None:
            print(self.connection_error or "database connection failed")
            return -1
        try:
            query = "INSERT INTO darshan (bookname, status) VALUES (%s, %s)"
            self.mycursor.execute(query, (name, "available"))
            self.conn.commit()
            return 1
        except Exception as e:
            print("Insert Error:", e)
            self.conn.rollback()
            return -1

    def all_books(self):
        if self.conn is None or self.mycursor is None:
            print(self.connection_error or "database connection failed")
            return []
        try:
            self.mycursor.execute("SELECT * FROM darshan ORDER BY bookname")
            return self.mycursor.fetchall()
        except Exception as e:
            print("Fetch Error:", e)
            return []

    def books(self):
        if self.conn is None or self.mycursor is None:
            print(self.connection_error or "database connection failed")
            return []
        try:
            self.mycursor.execute("SELECT * FROM darshan WHERE status = 'available'")
            return self.mycursor.fetchall()
        except Exception as e:
            print("Fetch Error:", e)
            return []

    def issue(self, bookname, issuedby, fined, days):
        if self.conn is None or self.mycursor is None:
            print(self.connection_error or "database connection failed")
            return 0

        try:
            self.mycursor.execute("SELECT status FROM darshan WHERE bookname = %s", (bookname,))
            row = self.mycursor.fetchone()

            if row is None:
                print("Book is not present in library.")
                return 0

            if row[0] != "available":
                print("Book is already issued.")
                return 0

            query = """
                UPDATE darshan
                SET status = %s, issuedby = %s, fined = %s, days = %s
                WHERE bookname = %s
            """
            self.mycursor.execute(query, ("unavailable", issuedby, fined, days, bookname))
            self.conn.commit()
            print("Book is issued.")
            return 1
        except Exception as e:
            print("Update Error:", e)
            self.conn.rollback()
            return -1