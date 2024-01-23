import requests
import pandas as pd
import streamlit as st


# @st.cache_resource
def main():
    col1, col2 = st.columns([77, 23])

    if 'button_clicked' not in st.session_state:
        st.session_state.button_clicked = False

    with col1:
        st.text_input("Search by ID", key="ann_id")
        st.text_input("Search by tags", key="tags")
        st.text_input("Search document", key="document")
        st.text_input("Max number of results", 20, key="max_results")
        if "ann_id" not in st.session_state:
            st.session_state.ann_id = ""
        if "tags" not in st.session_state:
            st.session_state.tags = ""
        if "document" not in st.session_state:
            st.session_state.document = ""
        if "max_results" not in st.session_state:
            st.session_state.max_results = 10

        if st.session_state.ann_id:
            url = f"http://localhost:8000/search_id?" \
                  f"ann_id={st.session_state.ann_id}"
            response = requests.get(url, verify=False)
            df = pd.read_json(response.json())
            st.dataframe(df)
        if st.session_state.tags:
            url = f"http://localhost:8000/search_tags?" \
                  f"tags={st.session_state.tags}"
            response = requests.get(url, verify=False)
            df = pd.read_json(response.json())
            st.text(
                f"Showing {len(df)} results with tag "
                f"'{str(st.session_state.tags)}'")
            st.dataframe(df)
        if st.session_state.document:
            if st.session_state.max_results == "":
                st.write('<span style="color:red">Please specify above the max'
                         ' number of results to be returned!</span>',
                         unsafe_allow_html=True
                         )
            else:
                url = f"http://localhost:8000/search_text?" \
                      f"text={st.session_state.document}&" \
                      f"max_results={st.session_state.max_results}"
                response = requests.get(url, verify=False)
                df = pd.read_json(response.json())
                df.index = range(1, len(df) + 1)
                st.write(
                    f"Found {len(df)} results with text "
                    f"'{str(st.session_state.document)}'")
                st.dataframe(df, height=(len(df) + 1) * 35 + 5)
    with col2:
        st.write("Most popular tags")
        response = get_popular_tags()
        col3, col4 = st.columns([1, 1])
        with col3:
            i = 0
            if st.button(
                    fr"{response['tags'][i][0]}:({response['tags'][i][1]})"):
                button_click(col1, response['tags'][i][0])
            if st.button(
                    fr"{response['tags'][i + 2][0]}:({response['tags'][i + 2][1]})"):
                button_click(col1, response['tags'][i + 2][0])
            if st.button(
                    fr"{response['tags'][i + 4][0]}:({response['tags'][i + 4][1]})"):
                button_click(col1, response['tags'][i + 4][0])
            if st.button(
                    fr"{response['tags'][i + 6][0]}:({response['tags'][i + 6][1]})"):
                button_click(col1, response['tags'][i + 6][0])
            if st.button(
                    fr"{response['tags'][i + 8][0]}:({response['tags'][i + 8][1]})"):
                button_click(col1, response['tags'][i + 8][0])
        with col4:
            i = 1
            if st.button(
                    fr"{response['tags'][i][0]}:({response['tags'][i][1]})"):
                button_click(col1, response['tags'][i][0])
            if st.button(
                    fr"{response['tags'][i + 2][0]}:({response['tags'][i + 2][1]})"):
                button_click(col1, response['tags'][i + 2][0])
            if st.button(
                    fr"{response['tags'][i + 4][0]}:({response['tags'][i + 4][1]})"):
                button_click(col1, response['tags'][i + 4][0])
            if st.button(
                    fr"{response['tags'][i + 6][0]}:({response['tags'][i + 6][1]})"):
                button_click(col1, response['tags'][i + 6][0])
            if st.button(
                    fr"{response['tags'][i + 8][0]}:({response['tags'][i + 8][1]})"):
                button_click(col1, response['tags'][i + 8][0])


def button_click(col, label: str):
    url = fr"http://localhost:8000/search_tags?tags={label}"
    response = requests.get(url, verify=False)
    df = pd.read_json(response.json())
    df.index = range(1, len(df) + 1)
    col.text(fr"Showing entries with tags {label}")
    col.write(df)


@st.cache_resource
def get_popular_tags():
    url = f"http://localhost:8000/dbop?mostpopulartags=0"
    return requests.get(url, verify=False).json()


if __name__ == '__main__':
    main()
