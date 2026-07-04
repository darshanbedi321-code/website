import streamlit as st
from email_validator import validate_email,EmailNotValidError
from database import Database 
db= Database()
st.sidebar.title("menu")
st.title("LOG IN FORM")

st.header("enter your information")
# st.subheader("this is subheading")
# st.text("this is python code")
# st.write("this is write code")
# st.markdown("this is markdown")
# # bold by **this is markdown
# # html code in markdown
# st.markdown("<h1 style= 'text-align: left;'>go went gone</h1>",unsafe_allow_html=True)
# # imput options
name=st.text_input("enter your name")
# st.write(name)
# age= st.number_input("enter your age",1,100)
age= st.slider("enter any number",1,100)

email= st.text_area("enter your email id")
password= st.text_input("enter password")
if st.button("verify"):
    if not email:
        st.warning("first enter your email")
    else:
        with st.spinner("checking your email..."):
            try:
                valid= validate_email(email,check_deliverability=False)
                db.store(name,age,email,password)
                st.write("welcome")
            except EmailNotValidError as e:
                st.error(f"invalid {e}")
                st.info("retry after entering correct email")

# st.text_area("enter comments")
# if st.button("click me"):
#     st.write("button is clicked")
# lang= ["java","c++","python"]
# st.radio("select any one",lang)
# st.selectbox("select something",lang)
# st.multiselect("selects skills",lang)
# from PIL import Image
# img= Image.open("pie.png")
# st.image(img,width= "stretch")
# # number and stretch full screan
# import pandas as pd
# df= {
#     "name":["darshan","sumit","ram"],
#     "age":[34,23,23],
#     "marks": [45,78,23]
# }
# df= pd.DataFrame(df)
# st.dataframe(df)
# st.table(df)
# st.line_chart(df[["age"]])
# st.bar_chart(df["marks"])
# file=st.file_uploader("upload file")
# file= pd.read_csv(file)
# st.write(file.head())


