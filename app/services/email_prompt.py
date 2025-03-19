prompt = """
Given the following input text {transcribed_text}, generate an email by following these steps:

Note: recipient_email is {recipient_email}. Use appropriate tools to fetch the current time if the text mentions time-related words (e.g., "tomorrow", "yesterday", etc.).

1. **Recipient Extraction:**  
   - If recipient_email is provided, use it as the recipient address.  
   - Otherwise, extract the recipient’s email address from {transcribed_text}.  
   - If no email is explicitly mentioned but a name appears, call the contact tool to look up the corresponding email address.

2. **Subject Formulation:**  
   - Analyze {transcribed_text} to identify the primary topic or purpose.  
   - Create a concise subject line that reflects the email’s intent.

3. **Email Body Creation:**  
   - Compose a professional email body that includes a greeting, the main message derived from {transcribed_text}, and an appropriate closing.  
   - Ensure the tone and style align with the provided context.

4. **Additional Context:**  
   - If extra details are needed to refine the subject or body, consult relevant web resources for further insights.

Output the email in the following structured JSON format. Do not include any extra text:
{
    "email": "[the recipient email address or None if not provided]",
    "recipient_name": "[the recipient name or None if not provided]",
    "email_body": "[email body goes here]",
    "explanation": "[if any field is necessary or if anything goes wrong, provide details here; otherwise, None]"
}
"""
