import streamlit as st
import requests

# Base URL for your FastAPI backend
API_URL = "http://localhost:8000"

# Inject Tailwind CSS via CDN and custom styles for background, container, and fonts
st.markdown(
    """
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
      body {
         background: #f3f4f6; /* Light gray background */
         font-family: 'Inter', sans-serif;
      }
      .container {
         max-width: 800px;
         margin: 0 auto;
         padding: 20px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state to store the API key after login
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = None

def login():
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.title("Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        payload = {"username": username, "password": password}
        try:
            # Send login credentials as JSON payload
            response = requests.post(f"{API_URL}/login", json=payload)
            response.raise_for_status()
            data = response.json()
            if data.get("ErrorCode") == 0:
                st.session_state['api_key'] = data["Data"]["api_key"]
                st.success("Logged in successfully!")
                st.rerun()  # Refresh to show the admin panel
            else:
                st.error(data.get("Message", "Login failed"))
        except Exception as e:
            st.error(f"Login error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

def fetch_queries():
    headers = {"X-API-Key": st.session_state['api_key']}
    try:
        response = requests.post(f"{API_URL}/support/queries/get", headers=headers)
        response.raise_for_status()
        data = response.json()
        queries = data["Data"].get("queries", [])
        return queries
    except Exception as e:
        st.error(f"Error fetching queries: {e}")
        return []

def reply_to_query(query_id, reply_text):
    headers = {"X-API-Key": st.session_state['api_key']}
    # Using the QueryReply model from your API (expects JSON with query_id and reply)
    payload = {"query_id": query_id, "reply": reply_text}
    try:
        response = requests.post(f"{API_URL}/support/queries/reply", json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        if result.get("ErrorCode") == 0:
            st.success("Reply sent successfully!")
        else:
            st.error("Failed to send reply.")
    except Exception as e:
        st.error(f"Error sending reply: {e}")

def render_query_card(query):
    # Set status badge styling based on query status
    status = query['status'].lower()
    if status == "open":
        badge = '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Open</span>'
    elif status == "closed":
        badge = '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">Closed</span>'
    else:
        badge = f'<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">{query["status"]}</span>'

    card_html = f"""
    <div class="bg-white shadow-lg rounded-lg p-6 my-4">
        <div class="flex justify-between items-center">
            <h3 class="text-2xl font-semibold">Query ID: {query['id']}</h3>
            {badge}
        </div>
        <p class="text-gray-700 mt-2 text-lg"><span class="font-medium">User ID:</span> {query['user_id']}</p>
        <p class="text-gray-700 mt-2 text-lg"><span class="font-medium">Query:</span> {query['query_text']}</p>
    """
    if query.get("reply"):
        card_html += f"""<p class="text-gray-700 mt-2 text-lg"><span class="font-medium">Reply:</span> {query['reply']}</p>"""
    else:
        card_html += f"""<p class="text-gray-700 mt-2 text-lg"><span class="font-medium">Reply:</span> <em>Not yet replied</em></p>"""
    card_html += "</div>"
    return card_html

def show_queries():
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.title("User Queries")
    queries = fetch_queries()
    if not queries:
        st.info("No queries found")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Partition queries into open and closed lists
    open_queries = [q for q in queries if q["status"].lower() == "open"]
    closed_queries = [q for q in queries if q["status"].lower() == "closed"]

    # Two tabs for easy navigation
    tabs = st.tabs(["Open Queries", "Closed Queries"])

    with tabs[0]:
        st.markdown("<h2 class='text-2xl font-bold mb-4'>Open Queries</h2>", unsafe_allow_html=True)
        if not open_queries:
            st.info("No open queries found")
        else:
            for query in open_queries:
                st.markdown(render_query_card(query), unsafe_allow_html=True)
                # Expander for replying to an open query
                with st.expander("Reply to this query"):
                    reply_text = st.text_area("Your Reply", key=f"reply_{query['id']}")
                    if st.button("Send Reply", key=f"send_reply_{query['id']}"):
                        reply_to_query(query['id'], reply_text)
                        st.rerun()  # Refresh after reply to update the list

    with tabs[1]:
        st.markdown("<h2 class='text-2xl font-bold mb-4'>Closed Queries</h2>", unsafe_allow_html=True)
        if not closed_queries:
            st.info("No closed queries found")
        else:
            for query in closed_queries:
                st.markdown(render_query_card(query), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def fetch_feedbacks():
    headers = {"X-API-Key": st.session_state['api_key']}
    try:
        response = requests.post(f"{API_URL}/support/feedback/get_all", headers=headers)
        response.raise_for_status()
        data = response.json()
        # According to your updated API, feedbacks are in data["Data"] with key "feedbacks"
        feedbacks = data["Data"].get("feedbacks", [])
        return feedbacks
    except Exception as e:
        st.error(f"Error fetching feedbacks: {e}")
        return []

def render_feedback_card(feedback):
    # Updated card to include comment time and adjusted sizes/colors
    card_html = f"""
    <div class="bg-white shadow-xl rounded-lg p-6 my-4">
        <div class="flex justify-between items-center">
            <h3 class="text-2xl font-semibold text-gray-800">Name: {feedback['user_name']}</h3>
            <span class="px-3 py-1 text-sm font-semibold rounded-full bg-yellow-200 text-yellow-900">
                Rating: {feedback['rating']}
            </span>
        </div>
        <p class="text-gray-700 mt-2 text-lg"><span class="font-medium">User ID:</span> {feedback['user_id']}</p>
        <p class="text-gray-700 mt-2 text-lg"><span class="font-medium">Comment:</span> {feedback['comment']}</p>
        <p class="text-gray-500 mt-2 text-sm"><span class="font-medium">Time:</span> {feedback['comment_time']}</p>
    </div>
    """
    return card_html

def show_feedback():
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.title("Feedback")
    feedbacks = fetch_feedbacks()
    if not feedbacks:
        st.info("No feedbacks found")
    else:
        st.markdown("<h2 class='text-2xl font-bold mb-4'>User Feedbacks</h2>", unsafe_allow_html=True)
        for feedback in feedbacks:
            st.markdown(render_feedback_card(feedback), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    if st.session_state['api_key'] is None:
        login()
    else:
        st.sidebar.title("Admin Panel")
        page = st.sidebar.radio("Navigation", ["Queries", "Feedback"])
        if page == "Queries":
            show_queries()
        elif page == "Feedback":
            show_feedback()

if __name__ == "__main__":
    main()
