import streamlit as st

st.write("This page is for testing stuffs")


def proc():
    st.file_uploader('')


if __name__ == '__main__':
    option = st.selectbox(
        'Which folder would you like to upload to?',
        ('1 docx-raw', '2 docx-text-only'), on_change=proc)
    st.write('You selected:', option)
