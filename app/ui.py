import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Harri AI Assistant", page_icon="🤖")

st.title("🔐 Login to Harri AI Assistant")

# Session state for token
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "username" not in st.session_state:
    st.session_state.username = None

# Register or Login
auth_choice = st.radio("Choose action", ["Login", "Register"])

with st.form("auth_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit_auth = st.form_submit_button("Submit")

    if submit_auth and username and password:
        endpoint = "/login" if auth_choice == "Login" else "/register"
        try:
            res = requests.post(f"{API_BASE}{endpoint}", json={"username": username, "password": password})
            if res.status_code == 200:
                if auth_choice == "Login":
                    st.session_state.auth_token = res.json()["token"]
                    st.session_state.username = username
                    st.success("Logged in successfully.")
                else:
                    st.success("Registered successfully. Please login.")
            else:
                st.error(res.json().get("detail", "Something went wrong."))
        except Exception as e:
            st.error(f"Connection error: {e}")

# Show query UI if logged in
if st.session_state.auth_token:
    st.title(f"💬 Welcome, {st.session_state.username}")
    
    # Add tabs for different sections
    tab1, tab2 = st.tabs(["💬 Ask Questions", "📊 Chat History"])
    
    with tab1:
        st.write("Ask something below:")
        
        with st.form("query_form"):
            user_query = st.text_input("Enter your query:")
            submitted = st.form_submit_button("Submit")

    if submitted and user_query.strip():
        payload = {"query": user_query, "user_id": st.session_state.username}
        try:
            response = requests.post(f"{API_BASE}/query", json=payload)
            if response.status_code == 200:
                response_data = response.json()
                result = response_data.get("answer", "No response returned.")
                response_id = response_data.get("response_id", "")
                
                st.text_area("Assistant Response", value=result, height=200)
                
                # Feedback section
                if response_id:
                    st.write("---")
                    st.write("**Was this response helpful?**")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("👍 Helpful", key=f"helpful_{response_id}"):
                            feedback_data = {
                                "response_id": response_id,
                                "helpful": True,
                                "feedback_text": ""
                            }
                            feedback_response = requests.post(f"{API_BASE}/feedback", json=feedback_data)
                            if feedback_response.status_code == 200:
                                st.success("Thank you for your feedback!")
                            else:
                                st.error("Failed to submit feedback")
                    
                    with col2:
                        if st.button("👎 Not Helpful", key=f"not_helpful_{response_id}"):
                            feedback_text = st.text_input("Please tell us why:", key=f"feedback_text_{response_id}")
                            if st.button("Submit Feedback", key=f"submit_feedback_{response_id}"):
                                feedback_data = {
                                    "response_id": response_id,
                                    "helpful": False,
                                    "feedback_text": feedback_text
                                }
                                feedback_response = requests.post(f"{API_BASE}/feedback", json=feedback_data)
                                if feedback_response.status_code == 200:
                                    st.success("Thank you for your feedback!")
                                else:
                                    st.error("Failed to submit feedback")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"API Error: {e}")
    
    with tab2:
        st.write("### My Chat History")
        
        # Show current user's chat history only
        try:
            # Get current user's chat history
            logs_response = requests.get(f"{API_BASE}/logs?limit=100&user_id={st.session_state.username}")
            
            if logs_response.status_code == 200:
                logs = logs_response.json()
                
                if logs:
                    st.write(f"### Your Recent Interactions ({len(logs)} total)")
                    
                    for i, log in enumerate(logs):
                        with st.expander(f"Query {i+1}: {log['query'][:50]}... ({log['timestamp']})"):
                            st.write(f"**Query:** {log['query']}")
                            st.write(f"**Response:** {log['response']}")
                            st.write(f"**Type:** {log['query_type']}")
                            st.write(f"**Processing Time:** {log['processing_time']:.2f}s")
                            if log['sources']:
                                st.write(f"**Sources:** {', '.join(log['sources'])}")
                            if log['feedback']:
                                st.write(f"**Feedback:** {log['feedback']}")
                else:
                    st.info("You haven't made any queries yet. Start asking questions to see your chat history here!")
            else:
                st.error("Failed to retrieve your chat history")
        except Exception as e:
            st.error(f"Error loading chat history: {e}")
