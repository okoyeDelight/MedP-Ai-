import streamlit as st
import time

st.markdown("""
<style>
/* Try targeting the generic text area */
.stChatInput textarea {
    border: 5px solid red;
}
/* Try testing targetting streamlit default chat block */
[data-testid="stChatInput"] {
    max-width: 50% !important;
    margin: 0 auto !important;
}
</style>
""", unsafe_allow_html=True)
st.chat_input("Ask MedP-AI anything about medicine...")
