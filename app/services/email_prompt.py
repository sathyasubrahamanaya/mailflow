prompt = """
"Given the following input text {transcribed_text}, generate an email by following these steps:

 and recipient_email is {recipient_email}
use appropriate tools to get current time if they mention tomorrow and yesterday etc
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
  

Output the email in the following structured json format,Don't print anything extra: 
{{email:[the recipient email address or None if not provided],"recipient_name:[name or  None if not provided]","email_body"[email body goes here],"explanation":[if any field is necessory, anything goes wrong provide here else None]}} 

"""
