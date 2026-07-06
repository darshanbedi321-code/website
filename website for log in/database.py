import mysql.connector


class Database:
    def __init__(self):
        self.conn = None
        self.mycursor = None
        self.connection_error = None

        try:
            self.conn = mysql.connector.connect(
                host="switchback.proxy.rlwy.net",
                user="root",
                password="RZNFaLvqKSXbmeDxTGtmkKZRHLBkCxak",
                database="railway",
                port=33397,
            )
            self.mycursor = self.conn.cursor()
        except Exception as e:
            self.connection_error = str(e)

    def store(self, name, age, email, password=None):
        if self.conn is None or self.mycursor is None:
            return self.connection_error or "database connection failed"

        try:
            query = """
                INSERT INTO user_data (name, age, email, password)
                VALUES (%s, %s, %s, %s)
            """
            self.mycursor.execute(query, (name, age, email, password))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            return str(e)
        else:
            return "done"
        
