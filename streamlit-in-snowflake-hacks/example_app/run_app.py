import streamlit as st

from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import Session

# common utils
import datetime
import os
import json


### METADATA - DO NOT CHANGE RANDOMLY - start ###

# set up current session
def _get_session():
    try:
        return get_active_session()
    except Exception:
        snowflake_config = {
            # fill in your Snowflake account config
        }

        return Session.builder.configs(snowflake_config).create()

session = _get_session()
st.session_state.cached_session = session

# set up cached dates and graphics controller
if 'start_date' not in st.session_state:
    st.session_state.start_date = datetime.datetime.utcnow().date()

if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.datetime.utcnow().replace(microsecond=0, second=0, minute=0).time()

if 'end_date' not in st.session_state:
    st.session_state.end_date = (datetime.datetime.utcnow().replace(microsecond=0, second=0, minute=0)+datetime.timedelta(hours=1)).date()

if 'end_time' not in st.session_state:
    st.session_state.end_time = (datetime.datetime.utcnow().replace(microsecond=0, second=0, minute=0)+datetime.timedelta(hours=1)).time()

### METADATA - DO NOT CHANGE RANDOMLY - end ###


### ADD YOUR PAGE - start ###

# render pages
_p0 = st.Page("home.py", title="Home", icon="🍳")

pg = st.navigation({
        "Welcome!": [
            _p0, # home
        ],
})

### ADD YOUR PAGE - end ###

# run the Streamlit app
pg.run()
