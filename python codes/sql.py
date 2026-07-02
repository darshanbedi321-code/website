import mysql.connector

class Database:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(host="localhost", user="root", password="", database="library")
            self.mycursor = self.conn.cursor()
        except:
            print("error")
        else:
            print("data base is connected")

    
    def store(self,name):
        try:
            self.mycursor.execute("""
            INSERT INTO `books`(`id`, `bookname`, `statues`, `issuedby`, `fined`, `days`) VALUES (NULL,'{}',"available","",0,0)
    """.format(name))
            self.conn.commit()
        except:
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

        if name in data:
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
                