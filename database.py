import mysql.connector

class Database:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(host="switchback.proxy.rlwy.net", user="root", password="RZNFaLvqKSXbmeDxTGtmkKZRHLBkCxak", database="railways",port =33397)
            self.mycursor = self.conn.cursor()
        except:
            pass
        else:
            pass

    
    def store(self,name,age,email,password=None):
        try:
            self.mycursor.execute("""
            INSERT INTO `user_data`(`name`, `age`, `email`, `password`) VALUES ('{}',{},"{}","{}")
    """.format(name,age,email,password))
            self.conn.commit()
        except Exception as e:
            print("database error ",e)
        else:
            return 1