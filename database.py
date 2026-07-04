import mysql.connector

class Database:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(host="switchback.proxy.rlwy.net", user="root", password="RZNFaLvqKSXbmeDxTGtmkKZRHLBkCxak", database="railway",port =33397)
            self.mycursor = self.conn.cursor()
        except Exception as e:
            print(e)
            self.conn = None 
            self.mycursor = None
            
        else:
            pass

    
    def store(self,name,age,email,password=None):
        try:
            self.mycursor.execute("""
            INSERT INTO `user_data`(`name`, `age`, `email`, `password`) VALUES ('{}',{},"{}","{}")
    """.format(name,age,email,password))
            self.conn.commit()
        except Exception as e:
            return str(e)
        else:
            return "done"
        
