from django.core.mail import EmailMessage
from django.conf import settings
import environ

env = environ.Env()
environ.Env.read_env()

def send_email_to_team_lead(name, email, description):
    
    context = {
        'name': name,
        'description': description,
        'email': email
    }
    
    email_subject = 'Task has been assigned to your team'
    email_body = f'Description: {description}'
    
    email = EmailMessage(
        email_subject, email_body,
        settings.DEFAULT_FROM_EMAIL, [email,],
    )
    return email.send(fail_silently=False)