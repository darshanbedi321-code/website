import mysql.connector

class Database:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(host="localhost", user="root", password="", database="user_info")
            self.mycursor = self.conn.cursor()
        except:
            pass
        else:
            pass

    
    def store(self,name,age,email,password=None):
        try:
            self.mycursor.execute("""
            INSERT INTO `user data`(`name`, `age`, `email`, `password`) VALUES ('{}',{},"{}","{}")
    """.format(name,age,email,password))
            self.conn.commit()
        except Exception as e:
            print("database error ",e)
        else:
            return 1