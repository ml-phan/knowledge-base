from collections import Counter

import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode


# @st.cache_resource
def main():
    col1, col2 = st.columns([77, 23])

    if 'button_clicked' not in st.session_state:
        st.session_state.button_clicked = False
    if 'result_df' not in st.session_state:
        st.session_state.result_df = False
    if 'result_msg' not in st.session_state:
        st.session_state.result_msg = False
    if 'result_df_full' not in st.session_state:
        st.session_state.result_df_full = False
    with col1:
        st.header("Input tags or term to search")
        with st.form("Question", clear_on_submit=False):
            tag_col, term_col, start_col, num_result, buff = st.columns(
                [4, 4, 2.5, 2.5, 2])
            tag = tag_col.text_input('Tag')
            term = term_col.text_input("Term")
            start = start_col.number_input("Start", min_value=0,
                                           value=0,
                                           step=10)
            num_result = num_result.number_input("Number of results",
                                                 min_value=1,
                                                 step=10,
                                                 key="number",
                                                 value=20,
                                                 )
            submitted = st.form_submit_button("Combine Search")
        if submitted:
            if int(start) < 0:
                st.markdown(
                    "<span style='color: red;'>Start cannot be negative "
                    "</span>",
                    unsafe_allow_html=True)
            if num_result == "" or num_result == str(0):
                st.markdown(
                    "<span style='color: red;'>Enter a max result "
                    "> 0 </span>",
                    unsafe_allow_html=True)
            if not tag and not term:
                st.markdown(
                    "<span style='color: red;'>Enter something to "
                    "search</span>",
                    unsafe_allow_html=True)
            else:
                url = f"http://localhost:8000/search_combine?" \
                      f"tag={tag}&term={term}&start={start}&" \
                      f"num_result={num_result}"
                response = requests.get(url, verify=False).json()
                df = pd.read_json(response["dataframe"]).reset_index()
                df_full = pd.read_json(
                    response["dataframe_full"])
                df.index = range(response['start'],
                                 response['start'] + len(df))
                # df_full.index = range(response['start'],
                #                       response['start'] + len(df_full))
                st.session_state.result_msg = f"Found {response['hits']} " \
                    f"results with tag '{tag}' and term '{term}'.\n Showing " \
                    f"results {response['start']} to {response['end']}. "
                # st.dataframe(df, height=(len(df) + 1) * 35 + 5)
                st.session_state.result_df = df
                st.session_state.result_df_full = df_full
        if st.session_state.result_msg:
            st.text(st.session_state.result_msg)
        if isinstance(st.session_state.result_df, pd.DataFrame):
            gb = GridOptionsBuilder.from_dataframe(st.session_state.result_df)
            gb.configure_selection(
                'single')  # Enable single row selection
            grid_options = gb.build()

            # Display the DataFrame with AgGrid
            aggrid_response = AgGrid(st.session_state.result_df,
                                     gridOptions=grid_options,
                                     fit_columns_on_grid_load=True,
                                     container=col1
                                     # columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
                                     )
            if aggrid_response:
                selected = aggrid_response["selected_rows"]
                if selected:
                    selected_index = selected[0]["index"]
                    col1.dataframe(
                        st.session_state.result_df_full.iloc[selected_index],
                        use_container_width=True
                    )
                    # if len(df) > 0:
                    #     all_tags = [tag for sublist in df.Tags for tag in
                    #                 sublist]
                    #     tag_counts = Counter(all_tags)
                    #     most_common_tags = tag_counts.most_common(20)
                    #     labels, values = zip(*most_common_tags)
                    #     plt.figure(figsize=(10, 8))
                    #     plt.bar(labels, values)
                    #     plt.xlabel('Tags')
                    #     plt.ylabel('Frequency')
                    #     plt.title('Top 20 Most Common Tags')
                    #     plt.xticks(rotation=60)
                    #     plt.tight_layout()
                    #     st.pyplot(plt)
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
