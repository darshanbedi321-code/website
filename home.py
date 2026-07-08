import streamlit as st
st.title("this is home page")
col1,col2,col3 = st.columns(3)
with col1:
    col1= st.text_input("enter your name")
with col2:
    col2= st.text_input("enter your name")
with col3:
    col3= st.text_input("enter your name")