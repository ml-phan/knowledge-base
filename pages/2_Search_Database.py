from pathlib import Path

import pandas as pd
import streamlit as st
from modules.es_ingestion import *
from modules.search import *


# @st.cache_resource
def main(elastic_search):
    st.write("Search is supposed to happen here")
    st.text_input("Search by ID", key="ann_id")
    st.text_input("Search by tags", key="tags")
    st.text_input("Search document", key="document")
    if "ann_id" not in st.session_state:
        st.session_state.ann_id = ""
    if "tags" not in st.session_state:
        st.session_state.tags = ""

    if st.session_state.ann_id:
        response = search_id(elastic_search, st.session_state.ann_id)
        st.write(response)
        print(response)
    if st.session_state.tags:
        response = search_tag(elastic_search, [st.session_state.tags])
        st.write(response)
        print(response)


if __name__ == '__main__':
    if not st.session_state.docker_ready:
        database_file = list(Path(r"./data").glob("*document_es*.pickle"))[-1]
        database_df = pd.read_pickle(database_file)
        _ = es_ingestion(database_df)
        st.session_state.docker_ready = True
    elastic_search = Elasticsearch("http://localhost:9200")
    main(elastic_search)
