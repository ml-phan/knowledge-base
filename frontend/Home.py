import requests
import streamlit as st

from pathlib import Path

ROOT = Path.cwd().parent


def main():
    st.set_page_config(layout="wide",
                       page_title="Hypothes.is Search"
                       )
    st.markdown(
        """
        # Hypothes.is annotation database
        Powered by ElasticSearch
        - [Hypothes.is](https://hypothes.is/)
        - Our group is [BehSci](https://hypothes.is/groups/Jk8bYJdN/behsci)
    """
    )

    if not st.session_state.docker_ready:
        url = f"http://localhost:8000/docker_ready"
        response = requests.get(url, verify=False)
        if response.json():
            st.session_state.docker_ready = not st.session_state.docker_ready
        else:
            url = f"http://localhost:8000/start_es_docker"
            _ = requests.get(url, verify=False)
            st.session_state.docker_ready = not st.session_state.docker_ready

    if st.session_state.docker_ready:
        st.write("Docker is running.")


if __name__ == '__main__':
    if "docker_ready" not in st.session_state:
        st.session_state.docker_ready = False
    main()
