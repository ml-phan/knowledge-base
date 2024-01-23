import streamlit as st

st.write("This page is for testing stuffs")


if __name__ == '__main__':
    random_number = st.text_input("Random number", key="rn")

    if st.button("What is in the field?"):
        st.write(random_number == "")
    col1, col2 = st.columns([80, 20])
    with col1:
        st.text_input("This is column 1.")
    with col2:
        st.text_input("This is column 2.")
    text = "is:preprint"
    st.text(text)
