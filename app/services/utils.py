import re
def generate_email(text: str) -> dict:
    subject = "Email Generated from Voice Input"
    body = f"""
    Dear Recipient,
    
    {text}
    
    Best regards,
    MailFlow User
    """
    return {"subject": subject, "body": body}

def remove_escapes(text):
    # Remove literal '\n' escape sequences by replacing them with a space
    text = re.sub(r'\\n', ' ', text)
    # Remove remaining backslashes
    text = re.sub(r'\\', '', text)
    return text

def remove_think_sections(text):
    # Remove all content between <think> and </think>, including the tags
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

def clean_response(text):
    return remove_escapes(remove_think_sections(text))