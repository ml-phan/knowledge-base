import time
from io import BytesIO

import requests
import pandas as pd
import streamlit as st
from pathlib import Path


# @st.cache_resource
def main():
    st.write("### Current database")

    if "database" not in st.session_state:
        st.session_state.database = False
    start1 = time.perf_counter()
    url = f"http://localhost:8000/database_exists"
    response = requests.get(url, verify=False)
    result = response.json()
    # if response.status_code == 200:
    #     # The response is a Parquet file, so we load it into a DataFrame
    #     df = pd.read_parquet(BytesIO(response.content))
    #     # Display the DataFrame in Streamlit
    #     st.write(df)
    # else:
    #     st.write('Failed to download the DataFrame')


    end1 = time.perf_counter()
    st.text(f"Time for requests {end1 - start1} seconds")
    start2 = time.perf_counter()
    if result is None:
        st.write(f"No database found. Click update button to retrieve "
                 f"new database")
    else:
        df = pd.read_json(result)
        # path = r"C:\Users\phan\OneDrive\Documents\Study\PythonProjects\knowledge-base\data\hypothesis_document_es_20240220_010820.pickle"
        # df = pd.read_pickle(path)
        # path = r"C:\Users\phan\OneDrive\Documents\Study\PythonProjects\rse23\data\12421-0003.csv"
        # df = pd.read_csv(path)
        st.dataframe(df)

        st.session_state.database = not st.session_state.database
    end2 = time.perf_counter()
    st.text(f"Time for streamlit display {end2 - start2}")


if __name__ == '__main__':
    st.set_page_config(page_title="Review Database", layout="wide")
    main()
    if st.button("Update database"):
        url = f"http://localhost:8000/update_db"
        st.write("Updating database. "
                 "Please wait, this might take a few minutes.")
        response = requests.get(url, verify=False)
        st.success("Update completed!")
        st.session_state.database = not st.session_state.database
