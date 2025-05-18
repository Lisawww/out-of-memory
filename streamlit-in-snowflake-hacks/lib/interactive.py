# Import python packages
import streamlit as st

# cached Snowpark session
session = st.session_state.cached_session

def store_value(key):
    st.session_state[key] = st.session_state["_"+key]

def load_value(key):
    st.session_state["_"+key] = st.session_state[key]

@st.fragment
def run_custom_query(expander_title, text_area_label, query_label, query_text_default):
    with st.expander(expander_title, expanded=True):
        custom_query = st.text_area(text_area_label, query_text_default, height=300, max_chars=5000)
        _a_run_query = st.button(label="Run query!", key="_run_query_" + query_label, use_container_width=True)

        if custom_query.count(';') > 1:
            st.error("Can only run one query!")
        else:
            sanitized_custom_query = custom_query.replace(";", '') + " limit 300;"
            if _a_run_query:
                df_custom_query = session.sql(sanitized_custom_query).to_pandas()
                st.dataframe(df_custom_query)
