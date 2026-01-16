import re
from langchain_core.prompts import PromptTemplate
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



prompt_template = PromptTemplate(
    input_variables=["transcribed_text", "recipient_name", "recipient_email"],
    template="""I need to generate a professional email based on the following input text: {transcribed_text}

Follow these steps carefully:
1. Recipient Extraction:
   - If recipient_email is provided, use it as the recipient address.
   - Otherwise, extract the recipient's email address from the input text.
   - If no email is explicitly mentioned but a name appears, call the contact tool to look up the corresponding email address.

2. Subject Formulation:
   - Analyze the input text to identify the primary topic or purpose.
   - Create a concise subject line that reflects the email's intent.

3. Email Body Creation:
   - Compose a professional email body that includes a greeting, the main message derived from the input text, and an appropriate closing.
   - Ensure the tone and style align with the provided context.

4. Additional Context:
   - If extra details are needed to refine the subject or body, consult relevant web resources for further insights.

Output the email in the following structured JSON format. Do not include any extra text:
```json
{
    "email": "[the recipient email address or None if not provided]",
    "recipient_name": "[the recipient name or None if not provided]",
    "email_body": "[email body goes here]",
    "explanation": "[if any field is necessary or something goes wrong, provide details here; otherwise, None]"
}
```

Important instructions:
- Make sure your response is valid JSON
- Include all fields in the response
- If a field is not applicable, use null or an empty string
- Do not include any additional text outside the JSON
- Double-check that all quotes are properly closed
- Ensure proper comma placement between JSON fields

Example of correct JSON output:

{
    "email": "john.doe@example.com",
    "recipient_name": "John Doe",
    "email_body": "Dear John,\n\nI hope this email finds you well. ...",
    "explanation": null
}

else Json as
{
    "email": "jNone",
    "recipient_name": "None",
    "email_body": "Dear John,\n\nI hope this email finds you well. ...",
    "explanation": null
}

Now, generate the email based on the input text provided.
"""
)
