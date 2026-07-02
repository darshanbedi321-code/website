# ------------------library managment system -------------
# import pandas as pd 
# df = pd.DataFrame(columns=["book name","issued by ","fine","days"])
# 
class library:
    def __init__(self,library_name,librarian_name,address):
        self.library_name = library_name
        self.librariun_name = librarian_name
        self.address = address
        # self.username= username
        # self.days= days
        # self.fine = fine
        # self.bookname= bookname
        self.books = []


    def add_books(self,bookname):
        self.books.append(bookname)
        print("book name = ",bookname," is added in the library \nnow the total no of books is ",len(self.books),"\n")

    def get_books(self):
        if self.books :
            for book in self.books:
                print(book)
        else:
            print("no book is in library")
    
    def rent_books(self,name,days):
        if name in self.books:
            # username = input("enter ur name")
            self.books.remove(name)
            print("book",name,"issued for ",days,"days")
            self.calculate_fine(days)
        else:
            print("book name =",name, "is not in library")

    def calculate_fine(self,days):
        if(days<=7):
            print("no fine for first days ur total fine is 0")
        else:
            extra = days - 7
            print("total fine is ",extra*10)

#     def record(self,username,fine,bookname,days):
#         df.iloc[]= [bookname,username,fine,days]

    


obj = library("central_library","sumati","punjab")
obj.get_books()
obj.add_books("jassu")
obj.get_books()
obj.add_books("paan masala")
obj.get_books()
obj.rent_books("jassu",69)
obj.get_books()
obj.rent_books("i love u ",45)
obj.get_books()
obj.rent_books("paan masala",6)
obj.get_books()





