from pathlib import Path

import pandas as pd
import streamlit as st

st.write("This is where you review our database")


@st.cache_resource
def display_data_base():
    database_file = list(Path(r"data").glob("*document_es*.pickle"))[-1]
    df = pd.read_pickle(database_file)
    st.dataframe(df)
    st.write(f"Total Entries: {len(df)}")


if __name__ == '__main__':
    display_data_base()
    st.write()
    if st.button("Update database"):
        st.success("Update completed!")
