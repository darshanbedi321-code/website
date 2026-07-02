import streamlit as st
st.title("this is contact page")
tab1,tab2,tab3 = st.tabs(["charts","data","form"])
with tab1:
    st.write("dva chat ke srju")
with tab2:
    st.write("ala mera data le")
with tab3:
    st.write("form ta teri dhui ch pau")