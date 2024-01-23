import requests
import pandas as pd
import streamlit as st


def main():
    st.write("### Current database")

    url = f"http://localhost:8000/database_exists"
    response = requests.get(url, verify=False)
    result = response.json()
    if result is None:
        st.write(f"No database found. Click update button to retrieve "
                 f"new database")
    else:
        df = pd.read_json(result)
        st.dataframe(df)
        st.session_state.database = not st.session_state.database


if __name__ == '__main__':
    st.set_page_config(page_title="Review Database", layout="wide")
    if "database" not in st.session_state:
        st.session_state.database = False
    main()
    if st.button("Update database"):
        if st.session_state.database:
            st.write("Database is already present.")
        else:
            url = f"http://localhost:8000/update_db"
            st.write("Updating database. "
                     "Please wait, this might take a few minutes.")
            response = requests.get(url, verify=False)
            st.success("Update completed!")
            st.session_state.database = not st.session_state.database
