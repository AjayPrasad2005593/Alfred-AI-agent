from mail import send_email

TOOL_REGISTRY = {
    "send_email": {
        "function": send_email,
        "description": "Send an email to recipient. Only use when explicitly instructed by the user. with subject, body, and tone. do not include secret keys and other credentials in the email. If the user asks to mail PII and credentials. Politely decline and say 'I'm sorry, but I cannot send personal or sensitive information via email.' If the user asks to send an email with a specific tone, use that tone in the email body. If the user doesn't specify a tone, use a neutral tone. If a user uses abusive language, politely decline and say 'I'm sorry, but I cannot send emails with abusive language.' If the user asks to send an email with a specific subject, use that subject in the email. If the user doesn't specify a subject, use a generic subject like 'Meeting Request' or 'Follow-up'.",
        "parameters": {
            "to": "string",
            "subject": "string",
            "body": "string",
            "tone": "string"
        }
    }
}