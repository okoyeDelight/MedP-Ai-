import streamlit as st
st.set_page_config(layout="wide")

st.markdown("""
<style>
/* Streamlit Chat Input styling target */
.stChatInputContainer, [data-testid="stChatInput"] {
    max-width: 60% !important;
    margin: 0 auto !important;
    border-radius: 30px !important;
}

/* Flashing Light Effect via animation */
@keyframes flashLight {
    0%   { box-shadow: 0 0 10px #10b981; border-color: #10b981; }
    50%  { box-shadow: 0 0 20px #d97706, inset 0 0 10px #d97706; border-color: #d97706; }
    100% { box-shadow: 0 0 10px #10b981; border-color: #10b981; }
}

[data-testid="stChatInput"] {
    animation: flashLight 3s infinite alternate !important;
}

/* Gradient Text inside chat input */
.stChatInput textarea {
    background: linear-gradient(to right, red, orange, yellow, green, cyan, blue, violet);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)
st.chat_input("Testing colored flashing input")
