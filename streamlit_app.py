import streamlit as st
import requests

# Set up the title
st.title("Travel Planning Chatbot")

# URL for your Flask backend (make sure your Flask app is running)
BACKEND_URL = "https://travel-chatbot-6.onrender.com/chat"

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Display chat history
for chat in st.session_state['chat_history']:
    st.write(f"{chat['role']}: {chat['message']}")

# Input for user query
user_input = st.text_input("You:", key="user_input")

# Send message button
if st.button("Send"):
    if user_input:
        # Add user message to chat history
        st.session_state['chat_history'].append({"role": "You", "message": user_input})

        # Send user input to Flask backend
        response = requests.post(BACKEND_URL, json={"query": user_input})

        if response.status_code == 200:
            chatbot_response = response.json().get("response", "Sorry, I didn't understand that.")
            # Add chatbot response to chat history
            st.session_state['chat_history'].append({"role": "Chatbot", "message": chatbot_response})
        else:
            st.error(f"Error: {response.status_code}")
    else:
        st.error("Please enter a message.")

# Clear chat button
if st.button("Clear Chat"):
    st.session_state['chat_history'] = []
