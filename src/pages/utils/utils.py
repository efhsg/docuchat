import streamlit as st


def get_index(options, context):
    return (
        0
        if st.session_state[context] not in options
        else options.index(st.session_state[context])
    )
