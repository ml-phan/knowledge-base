import streamlit as st


def main():
    st.write("Hypothes.is Database")
    if "search_panel" not in st.session_state:
        st.session_state.search_panel = False

    def search_database():
        st.text_input("Tags", key="tags")
        st.text_input("Text", key="text")
        st.write("Search is not yet implemented!")

    def update_database():
        st.write("Update Done!")

    if st.sidebar.button("Update database"):
        update_database()

    st.sidebar.button("Search database", on_click=search_database)


def tutorial_1():
    st.title("Hello")
    if 'stage' not in st.session_state:
        st.session_state.stage = 0

    def set_state(i):
        st.session_state.stage = i

    if st.session_state.stage == 0:
        st.button('Begin', on_click=set_state, args=[1])

    if st.session_state.stage >= 1:
        name = st.text_input('Name', on_change=set_state, args=[2])

    if st.session_state.stage >= 2:
        st.write(f'Hello {name}!')
        color = st.selectbox(
            'Pick a Color',
            [None, 'red', 'orange', 'green', 'blue', 'violet'],
            on_change=set_state, args=[3]
        )
        if color is None:
            set_state(2)

    if st.session_state.stage >= 3:
        st.write(f':{color}[Thank you!]')
        st.button('Start Over', on_click=set_state, args=[0])


def hello():
    st.set_page_config(page_title="Hello")
    st.markdown(
        """
        # Hypothes.is annotation database
        Powered by ElasticSearch
        - [Hypothes.is](https://hypothes.is/)
        - Our group is [BehSci](https://hypothes.is/groups/Jk8bYJdN/behsci)
    """
    )
    if "docker_ready" not in st.session_state:
        st.session_state.docker_ready = False

    # if "elastic_search" not in st.session_state:
    #     st.session_state.elastic_search = None


if __name__ == '__main__':
    hello()
    # tutorial_1()
