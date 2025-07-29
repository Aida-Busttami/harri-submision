import streamlit as st
import requests
import json

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Harri AI Assistant", page_icon="🤖")

# Session state for authentication and navigation
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "show_main_app" not in st.session_state:
    st.session_state.show_main_app = False

# Main app function
def show_main_app():
    st.title(f"💬 Welcome, {st.session_state.username}")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 Chat", 
        "📊 My Chat History", 
        "📈 Conversation Statistics", 
        "🔍 System Observability Logs"
    ])
    
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
                    log_id = response_data.get("log_id")
                    
                    st.text_area("Assistant Response", value=result, height=200)
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"API Error: {e}")
    
    with tab2:
        st.write("### 📊 My Chat History")
        
        # Add refresh button
        if st.button("🔄 Refresh History", key="refresh_history"):
            st.rerun()
        
        # Show current user's chat history only
        try:
            # Get current user's chat history using the conversation context endpoint
            logs_response = requests.get(f"{API_BASE}/conversation/history/{st.session_state.username}?limit=100")
            
            if logs_response.status_code == 200:
                response_data = logs_response.json()
                logs = response_data.get('history', [])
                
                if logs:
                    # Add summary metrics at the top
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Interactions", len(logs))
                    
                    with col2:
                        # Count different query types
                        query_types = {}
                        for log in logs:
                            q_type = log.get('query_type', 'unknown')
                            query_types[q_type] = query_types.get(q_type, 0) + 1
                        most_common = max(query_types.items(), key=lambda x: x[1])[0] if query_types else "N/A"
                        st.metric("Most Common Type", most_common)
                    
                    with col3:
                        # Calculate average processing time
                        avg_time = sum(log.get('processing_time', 0) for log in logs) / len(logs) if logs else 0
                        st.metric("Avg Response Time", f"{avg_time:.2f}s")
                    
                    with col4:
                        # Count interactions with sources
                        with_sources = sum(1 for log in logs if log.get('sources') and len(log['sources']) > 0)
                        st.metric("With Sources", f"{with_sources}/{len(logs)}")
                    
                    st.write("---")
                    st.write(f"### Your Recent Interactions ({len(logs)} total)")
                    
                    for i, log in enumerate(logs):
                        # Format timestamp properly in UTC+3
                        timestamp = log['timestamp']
                        if isinstance(timestamp, str):
                            try:
                                from datetime import datetime
                                # Parse the timestamp string and convert to UTC+3
                                if 'T' in timestamp and 'Z' in timestamp:
                                    # ISO format with Z (UTC)
                                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                elif 'T' in timestamp and ('+' in timestamp or '-' in timestamp[-6:]):
                                    # ISO format with timezone offset
                                    dt = datetime.fromisoformat(timestamp)
                                elif 'T' in timestamp:
                                    # ISO format without timezone - assume UTC
                                    dt = datetime.fromisoformat(timestamp + '+00:00')
                                else:
                                    # Try parsing as regular datetime string - assume UTC
                                    dt = datetime.fromisoformat(timestamp + '+00:00')
                                
                                # Convert to UTC+3 (EEST/EET)
                                from datetime import timezone, timedelta
                                utc_plus_3 = timezone(timedelta(hours=3))
                                local_dt = dt.astimezone(utc_plus_3)
                                display_time = local_dt.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                display_time = timestamp
                        else:
                            # If it's a datetime object, convert to UTC+3
                            try:
                                from datetime import timezone, timedelta
                                utc_plus_3 = timezone(timedelta(hours=3))
                                local_dt = timestamp.astimezone(utc_plus_3)
                                display_time = local_dt.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                display_time = str(timestamp)
                        
                        # Check if feedback already exists for this log
                        has_feedback = False
                        feedback_status = None
                        if log.get('feedback'):
                            has_feedback = True
                            try:
                                if isinstance(log['feedback'], str):
                                    feedback_data = json.loads(log['feedback'])
                                else:
                                    feedback_data = log['feedback']
                                
                                if isinstance(feedback_data, dict):
                                    feedback_status = feedback_data.get('helpful', 'Unknown')
                            except:
                                feedback_status = 'Unknown'
                        
                        # Create columns for message and feedback buttons
                        col_msg, col_feedback = st.columns([4, 1])
                        
                        with col_msg:
                            with st.expander(f"Query {i+1}: {log['query'][:50]}... ({display_time})"):
                                st.write(f"**Query:** {log['query']}")
                                st.write(f"**Response:** {log['response']}")
                                st.write(f"**Type:** {log['query_type']}")
                                st.write(f"**Processing Time:** {log['processing_time']:.2f}s")
                                if log['sources'] and len(log['sources']) > 0:
                                    st.write(f"**Sources:** {', '.join(log['sources'])}")
                                
                                # Enhanced feedback display
                                if log.get('feedback'):
                                    st.write("---")
                                    st.write("**📝 User Feedback:**")
                                    try:
                                        # Try to parse feedback as JSON
                                        if isinstance(log['feedback'], str):
                                            feedback_data = json.loads(log['feedback'])
                                        else:
                                            feedback_data = log['feedback']
                                        
                                        helpful = feedback_data.get('helpful', 'Unknown')
                                        feedback_text = feedback_data.get('feedback_text', '')
                                        
                                        # Display helpful status with emoji
                                        if helpful is True:
                                            st.write("👍 **Helpful**")
                                        elif helpful is False:
                                            st.write("👎 **Not Helpful**")
                                        else:
                                            st.write(f"**Status:** {helpful}")
                                        
                                        # Display feedback text if provided
                                        if feedback_text:
                                            st.write(f"**Comment:** {feedback_text}")
                                    except (json.JSONDecodeError, TypeError):
                                        # If not JSON, display as string
                                        st.write(f"**Feedback:** {log['feedback']}")
                         
                        with col_feedback:
                            log_id = log.get('id')
                            if log_id:
                                if has_feedback:
                                    # Show feedback status
                                    if feedback_status is True:
                                        st.write("👍")
                                        st.caption("Helpful")
                                    elif feedback_status is False:
                                        st.write("👎")
                                        st.caption("Not Helpful")
                                    else:
                                        st.write("📝")
                                        st.caption("Feedback")
                                else:
                                    # Show feedback buttons
                                    st.write("**Feedback:**")
                                    
                                    # Helpful button
                                    if st.button("👍", key=f"helpful_{log_id}", help="Mark as helpful"):
                                        feedback_data = {
                                            "log_id": log_id,
                                            "helpful": True,
                                            "feedback_text": ""
                                        }
                                        feedback_response = requests.post(f"{API_BASE}/feedback", json=feedback_data)
                                        if feedback_response.status_code == 200:
                                            st.success("Thank you!")
                                            st.rerun()
                                        else:
                                            st.error("Failed")
                                    
                                    # Not helpful button
                                    if st.button("👎", key=f"not_helpful_{log_id}", help="Mark as not helpful"):
                                        st.session_state[f"show_feedback_{log_id}"] = True
                                        st.rerun()
                                    
                                    # Show feedback text input if "Not Helpful" was clicked
                                    if st.session_state.get(f"show_feedback_{log_id}", False):
                                        feedback_text = st.text_input("Why not helpful?", key=f"feedback_text_{log_id}")
                                        if st.button("Submit", key=f"submit_feedback_{log_id}"):
                                            feedback_data = {
                                                "log_id": log_id,
                                                "helpful": False,
                                                "feedback_text": feedback_text
                                            }
                                            feedback_response = requests.post(f"{API_BASE}/feedback", json=feedback_data)
                                            if feedback_response.status_code == 200:
                                                st.success("Thank you!")
                                                st.session_state[f"show_feedback_{log_id}"] = False
                                                st.rerun()
                                            else:
                                                st.error("Failed")
                else:
                    st.info("You haven't made any queries yet. Start asking questions to see your chat history here!")
            else:
                st.error("Failed to retrieve your chat history")
        except Exception as e:
            st.error(f"Error loading chat history: {e}")
    
    with tab3:
        st.write("### 📈 Conversation Statistics")
        
        # Add refresh button
        if st.button("🔄 Refresh Stats", key="refresh_stats"):
            st.rerun()
        
        try:
            # Get conversation statistics for current user
            stats_response = requests.get(f"{API_BASE}/conversation/stats/{st.session_state.username}")
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                stats = stats_data.get('stats', {})
                
                # Display statistics in a nice format
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Total Conversations",
                        value=stats.get('total_conversations', 0),
                        help="Total number of conversations with the AI"
                    )
                
                with col2:
                    st.metric(
                        label="Recent (24h)",
                        value=stats.get('recent_conversations_24h', 0),
                        help="Conversations in the last 24 hours"
                    )
                
                with col3:
                    # Calculate average processing time if available
                    avg_time = "N/A"
                    if stats.get('total_conversations', 0) > 0:
                        # This would need to be calculated from the logs
                        avg_time = "~5s"  # Placeholder
                    
                    st.metric(
                        label="Avg Response Time",
                        value=avg_time,
                        help="Average time to generate responses"
                    )
                
                # Query type distribution
                st.write("### Query Type Distribution")
                query_types = stats.get('query_type_distribution', {})
                
                if query_types:
                    # Create a bar chart
                    import pandas as pd
                    df = pd.DataFrame(list(query_types.items()), columns=['Query Type', 'Count'])
                    
                    # Add some styling to the query types
                    df['Query Type'] = df['Query Type'].map({
                        'in_scope': '✅ In Scope',
                        'out_of_scope': '❌ Out of Scope',
                        'dynamic_data': '🔄 Dynamic Data',
                        'error': '⚠️ Error'
                    }).fillna(df['Query Type'])
                    
                    st.bar_chart(df.set_index('Query Type'))
                    
                    # Display as table as well
                    st.write("### Detailed Breakdown")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No query data available yet. Start asking questions to see statistics!")
                
                # Additional insights
                st.write("### 💡 Insights")
                total = stats.get('total_conversations', 0)
                recent = stats.get('recent_conversations_24h', 0)
                
                if total > 0:
                    if recent > 0:
                        st.success(f"🎉 You've been active today! {recent} conversations in the last 24 hours.")
                    
                    if total >= 10:
                        st.info("🌟 You're a power user! You've had 10+ conversations with the AI.")
                    elif total >= 5:
                        st.info("📈 You're getting comfortable with the AI assistant.")
                    else:
                        st.info("🚀 You're just getting started! Keep asking questions to unlock more insights.")
                else:
                    st.info("👋 Welcome! Start asking questions to see your conversation statistics here.")
                    
            else:
                st.error("Failed to retrieve conversation statistics")
        except Exception as e:
            st.error(f"Error loading conversation statistics: {e}")
    
    with tab4:
        st.write("### System Observability Logs")
        
        # Add refresh button
        if st.button("🔄 Refresh Logs"):
            st.rerun()
        
        try:
            # Get observability logs (fixed limit of 50)
            logs_response = requests.get(f"{API_BASE}/observability/logs?limit=50")
            
            if logs_response.status_code == 200:
                logs_data = logs_response.json()
                logs = logs_data.get('logs', [])
                
                if logs:
                    st.write(f"### Recent System Actions ({len(logs)} total)")
                    
                    # Add action filter
                    action_filter = st.selectbox(
                        "Filter by Action Type:",
                        ["All"] + list(set(log['action'] for log in logs))
                    )
                    
                    # Filter logs by action type
                    filtered_logs = logs
                    if action_filter != "All":
                        filtered_logs = [log for log in logs if log['action'] == action_filter]
                    
                    # Display logs
                    for i, log in enumerate(filtered_logs):
                        timestamp = log.get('timestamp', 'Unknown')
                        
                        if isinstance(timestamp, str):
                            try:
                                from datetime import datetime
                                # Parse the timestamp string and convert to UTC+3
                                if 'T' in timestamp and 'Z' in timestamp:
                                    # ISO format with Z (UTC)
                                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                elif 'T' in timestamp and ('+' in timestamp or '-' in timestamp[-6:]):
                                    # ISO format with timezone offset
                                    dt = datetime.fromisoformat(timestamp)
                                elif 'T' in timestamp:
                                    # ISO format without timezone - assume UTC
                                    dt = datetime.fromisoformat(timestamp + '+00:00')
                                else:
                                    # Try parsing as regular datetime string - assume UTC
                                    dt = datetime.fromisoformat(timestamp + '+00:00')
                                
                                # Convert to UTC+3 (EEST/EET)
                                from datetime import timezone, timedelta
                                utc_plus_3 = timezone(timedelta(hours=3))
                                local_dt = dt.astimezone(utc_plus_3)
                                display_time = local_dt.strftime('%Y-%m-%d %H:%M:%S')
                            except Exception as e:
                                display_time = str(timestamp)
                        else:
                            display_time = str(timestamp)
                        
                        # Color code based on action type - more intuitive logic
                        action = log.get('action', 'Unknown')
                        if 'error' in action.lower():
                            color = "🔴"  # Red for errors
                        elif 'completed' in action.lower() or 'success' in action.lower():
                            color = "🟢"  # Green for successful completions
                        elif 'started' in action.lower() or 'received' in action.lower():
                            color = "🟡"  # Yellow for starting/initiation
                        elif 'tool' in action.lower():
                            color = "🔵"  # Blue for tool operations
                        elif 'search' in action.lower() or 'knowledge' in action.lower():
                            color = "🟣"  # Purple for knowledge/search operations
                        elif 'processing' in action.lower():
                            color = "🟠"  # Orange for processing steps
                        else:
                            color = "⚪"  # White for other actions
                        
                        with st.expander(f"{color} {action} - {display_time}"):
                            st.write(f"**Action:** {action}")
                            st.write(f"**Query:** {log.get('query', 'N/A')[:100]}...")
                            st.write(f"**Timestamp:** {display_time}")
                            
                            duration = log.get('duration')
                            if duration is not None:
                                st.write(f"**Duration:** {duration:.3f}s")
                            
                            result = log.get('result')
                            if result:
                                st.write(f"**Result:** {result}")
                            
                            error = log.get('error')
                            if error:
                                st.write(f"**Error:** {error}")
                    

                else:
                    st.info("No system logs available yet.")
            else:
                st.error("Failed to retrieve system logs")
        except Exception as e:
            st.error(f"Error loading system logs: {e}")
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.auth_token = None
        st.session_state.username = None
        st.session_state.show_main_app = False
        st.rerun()

# Authentication page
def show_auth_page():
    st.title("🔐 Login to Harri AI Assistant")

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
                    st.session_state.show_main_app = True
                    st.success("Logged in successfully! Redirecting...")
                    st.rerun()
                else:
                    st.success("Registered successfully. Please login.")
            else:
                st.error(res.json().get("detail", "Something went wrong."))
        except Exception as e:
            st.error(f"Connection error: {e}")

# Main app logic
if st.session_state.show_main_app and st.session_state.auth_token:
    show_main_app()
else:
    show_auth_page()
