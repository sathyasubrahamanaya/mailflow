def generate_email(text: str) -> dict:
    subject = "Email Generated from Voice Input"
    body = f"""
    Dear Recipient,
    
    {text}
    
    Best regards,
    MailFlow User
    """
    return {"subject": subject, "body": body}
