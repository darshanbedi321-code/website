import mysql.connector


class Database:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host="hayabusa.proxy.rlwy.net",
                user="root",
                password="JnYnJDYBMWmaAYzOFQAVPOxMKbnhMYSD",
                database="railway",
                port=56787,
            )
            self.mycursor = self.conn.cursor()
        except Exception as e:
            self.connection_error = str(e)

    def store(self,name):
        if self.conn is None or self.mycursor is None:
            return self.connection_error or "database connection failed"

        try:
            query = """
                INSERT INTO books (bookname, statues)
                VALUES (%s, %s)
            """
            self.mycursor.execute(query, (name, "available"))
            self.conn.commit()
        except Exception:
            return -1
        else:
            return 1
        
    def books(self):
        try:
            self.mycursor.execute("""SELECT * FROM books WHERE statues = 'available'""")
            data=self.mycursor.fetchall()
            return data
        except:
            print("error occur")

    def issue(self, name, issuedby, fined, days):
        data = self.books()

        if any(name == row[1] for row in data):
            try:
                query = """
                UPDATE books
                SET statues = %s,
                    issuedby = %s,
                    fined = %s,
                    days = %s
                WHERE bookname = %s
                """

                self.mycursor.execute(
                    query,
                    ("unavailable", issuedby, fined, days, name)
                )

                self.conn.commit()
                print("Book is issued.")

            except Exception as e:
                print("Error:", e)

        else:
            print("Book is not present in library.")
                