import streamlit as st

st.write("This page is for testing stuffs")

if __name__ == '__main__':
    random_number = st.text_input("Random number", key="rn")
    input_key = 'text_input'
    if input_key not in st.session_state:
        st.session_state[input_key] = ""

    if st.button("What is in the field?"):
        st.write(random_number == "")
    col1, col2 = st.columns([80, 20])
    with col1:
        st.text_input("This is column 1.")
    with col2:
        st.text_input("This is column 2.")
    text = "is:preprint"
    st.text(text)

    with st.form("Question", clear_on_submit=False):
        buff, col, buff2 = st.columns([1, 1, 4])
        tag = buff.text_input('smaller text window:')
        keyword = col.text_input("Ask a question:")
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write(tag)

    if 'number' not in st.session_state:
        st.session_state['number'] = 10
    placeholder = st.empty()
    test_button = st.button("Change value")
    show_button = st.button("Show value")
    if test_button:
        st.session_state["number"] += 300
        st.text(st.session_state["number"])
    if show_button:
        st.text(st.session_state["number"])
    number_input = placeholder.number_input("Random number", key="number",
                                   value=st.session_state["number"])
