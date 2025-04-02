import streamlit as st
import requests
import json
import urllib.parse

# Base URL of your FastAPI backend
BASE_URL = "http://localhost:8000"  # update as needed

# Initialize session state variables
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "username" not in st.session_state:
    st.session_state.username = None

def is_nonempty_audio(audio):
    """Helper function to check if audio data is nonempty."""
    if audio is None:
        return False
    try:
        # If audio has a getbuffer() method (e.g. BytesIO)
        if hasattr(audio, "getbuffer"):
            return audio.getbuffer().nbytes > 0
        # Otherwise, if audio is bytes-like, try using len()
        return len(audio) > 0
    except Exception:
        return False

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Register", "Login", "Contacts", "Email Composer"])

# --------------------
# Registration Page
# --------------------
if page == "Register":
    st.title("User Registration")
    with st.form("register_form"):
        name = st.text_input("Name")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Register")
    
    if submitted:
        payload = {
            "name": name,
            "username": username,
            "email": email,
            "password": password
        }
        try:
            response = requests.post(f"{BASE_URL}/register", json=payload)
            data = response.json()
            if data.get("ErrorCode") == 0:
                st.success(f"Registration successful! User ID: {data['Data']['user_id']}")
            else:
                st.error(f"Registration failed: {data.get('Message', 'Unknown error')}")
        except Exception as e:
            st.error(f"Error: {e}")

# --------------------
# Login Page
# --------------------
elif page == "Login":
    st.title("User Login")
    with st.form("login_form"):
        login_username = st.text_input("Username")
        login_password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
    
    if submitted:
        payload = {
            "username": login_username,
            "password": login_password
        }
        try:
            response = requests.post(f"{BASE_URL}/login", json=payload)
            data = response.json()
            if data.get("ErrorCode") == 0:
                st.session_state.api_key = data["Data"]["api_key"]
                st.session_state.username = login_username
                st.success("Login successful!")
            else:
                st.error(f"Login failed: {data.get('Message', 'Unknown error')}")
        except Exception as e:
            st.error(f"Error: {e}")

# --------------------
# Contacts Page
# --------------------
elif page == "Contacts":
    st.title("Contact Management")
    
    st.header("Add Contact")
    with st.form("add_contact_form"):
        contact_name = st.text_input("Contact Name")
        contact_email = st.text_input("Contact Email")
        contact_phone = st.text_input("Contact Phone")
        submitted = st.form_submit_button("Add Contact")
    
    if submitted:
        headers = {"X-API-Key": st.session_state.api_key}
        payload = {
            "name": contact_name,
            "email": contact_email,
            "phone": contact_phone
        }
        try:
            response = requests.post(f"{BASE_URL}/contacts/create", json=payload, headers=headers)
            data = response.json()
            if data.get("ErrorCode") == 0:
                st.success("Contact added successfully!")
            else:
                st.error(f"Failed to add contact: {data.get('Message', 'Unknown error')}")
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.header("List Contacts")
    if st.button("Refresh Contacts"):
        headers = {"X-API-Key": st.session_state.api_key}
        try:
            response = requests.get(f"{BASE_URL}/contacts/get", headers=headers)
            data = response.json()
            if data.get("ErrorCode") == 0:
                contacts = data.get("Data", {}).get("contacts", [])
                st.write(contacts)
            else:
                st.error(f"Failed to retrieve contacts: {data.get('Message', 'Unknown error')}")
        except Exception as e:
            st.error(f"Error: {e}")

# --------------------
# Email Composer Page
# --------------------
elif page == "Email Composer":
    st.title("Compose & Send Email")
    
    if not st.session_state.api_key:
        st.warning("Please log in first to access the email composer.")
    else:
        st.subheader("Record Audio")
        # Use st.audio_input to record audio from the user's microphone.
        recorded_audio = st.audio_input("Record your message")
        if recorded_audio:
            st.audio(recorded_audio)

        st.subheader("Or Upload Audio File")
        uploaded_file = st.file_uploader("Upload Voice Recording (MP3, WAV, or M4A)", type=["mp3", "wav", "m4a"])
        
        # Choose which audio to use: if recorded audio is nonempty, prefer it; otherwise, use the uploaded file.
        final_audio = recorded_audio if is_nonempty_audio(recorded_audio) else uploaded_file

        with st.form("email_form"):
            st.subheader("Email Details")
            transcribed_text = st.text_area("Enter transcribed text / additional instructions", height=100)
            recipient_name = st.text_input("Recipient Name (optional)")
            recipient_email = st.text_input("Recipient Email")
            generate_email_button = st.form_submit_button("Generate Email")
        
        def generate_email_request(transcribed_text, recipient_name, recipient_email, audio_file=None):
            files = {}
            data = {
                "transcribed_text": transcribed_text,
                "recipient_name": recipient_name,
                "recipient_email": recipient_email
            }
            if audio_file is not None:
                file_name = audio_file.name if hasattr(audio_file, "name") else "recording.mp3"
                file_bytes = audio_file.getvalue() if hasattr(audio_file, "getvalue") else audio_file
                # Use provided content type if available; otherwise default to "audio/mp3"
                content_type = audio_file.type if hasattr(audio_file, "type") else "audio/mp3"
                files["file"] = (file_name, file_bytes, content_type)
            headers = {"X-API-Key": st.session_state.api_key}
            try:
                response = requests.post(
                    f"{BASE_URL}/email/generate",
                    data=data,
                    files=files,
                    headers=headers
                )
                return response.json()
            except Exception as e:
                st.error(f"Request failed: {e}")
                return None

        if generate_email_button:
            email_resp = generate_email_request(transcribed_text, recipient_name, recipient_email, final_audio)
            if email_resp and email_resp.get("ErrorCode") == 0:
                email_content = email_resp["Data"]["email_content"]
                st.success("Email generated successfully!")
                st.write("**Subject:**", email_content.get("subject"))
                st.write("**Body:**", email_content.get("body"))
                st.write("**Explanation:**", email_content.get("explanation"))
                
                # Ensure URL parameters are strings before encoding.
                subject = str(email_content.get("subject", ""))
                body = str(email_content.get("body", ""))
                recipient_email_str = str(recipient_email)
                
                gmail_url = (
                    "https://mail.google.com/mail/?view=cm&fs=1"
                    f"&to={urllib.parse.quote(recipient_email_str)}"
                    f"&su={urllib.parse.quote(subject)}"
                    f"&body={urllib.parse.quote(body)}"
                    "&bcc=someone.else@example.com"
                )
                st.markdown(f"[Send via Gmail]({gmail_url})", unsafe_allow_html=True)
                
                st.session_state.generated_instructions = transcribed_text
                st.session_state.recipient_name = recipient_name
                st.session_state.recipient_email = recipient_email
                st.session_state.audio_file = final_audio
                st.session_state.email_content = email_content
            else:
                st.error("Failed to generate email.")

        if "email_content" in st.session_state:
            st.subheader("Modify Generation Instructions")
            modified_instructions = st.text_area("Update instructions for email generation",
                                                 value=st.session_state.generated_instructions,
                                                 height=100)
            if st.button("Regenerate Email"):
                email_resp = generate_email_request(
                    modified_instructions,
                    st.session_state.recipient_name,
                    st.session_state.recipient_email,
                    None  # For regeneration, assume no audio file is needed.
                )
                if email_resp and email_resp.get("ErrorCode") == 0:
                    email_content = email_resp["Data"]["email_content"]
                    st.success("Email regenerated successfully!")
                    st.write("**To email** ",email_content.get("recipient_email",))
                    st.write("**Subject:**", email_content.get("subject"))
                    st.write("**Body:**", email_content.get("body"))
                    st.write("**Explanation:**", email_content.get("explanation"))
                    
                    subject = str(email_content.get("subject", ""))
                    body = str(email_content.get("body", ""))
                    if str(st.session_state.recipient_email):
                        recipient_email_str = str(st.session_state.recipient_email)
                    else:
                        recipient_email_str = email_content.get("recipient_email","")
                    
                    gmail_url = (
                        "https://mail.google.com/mail/?view=cm&fs=1"
                        f"&to={urllib.parse.quote(recipient_email_str)}"
                        f"&su={urllib.parse.quote(subject)}"
                        f"&body={urllib.parse.quote(body)}"
                       
                    )
                    st.markdown(f"[Send via Gmail]({gmail_url})", unsafe_allow_html=True)
                    
                    st.session_state.email_content = email_content
                    st.session_state.generated_instructions = modified_instructions
                else:
                    st.error("Failed to regenerate email.")
