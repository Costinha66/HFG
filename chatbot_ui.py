import streamlit as st
import openai
import os
from chatbot_logic import chatbot


# Streamlit UI
st.title("🤖❤️ CareConnect ❤️🤖")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input for new message
user_input = st.chat_input("Ask me anything...")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message in chat
    with st.chat_message("user"):
        st.markdown(user_input)

    ############################################################ CHATBOT ###############################################################
    response = chatbot(user_input)
    chatbot_reply = response.split("</think>")[1:][0]
    ####################################################################################################################################

    # Add chatbot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": chatbot_reply})

    # Display chatbot response
    with st.chat_message("assistant"):
        st.markdown(chatbot_reply)
