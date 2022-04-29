from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger
from project.emails.email import send_email_to_team_lead

logger = get_task_logger(__name__)
@shared_task
def add(x,y):
    return x+y

@shared_task(name="send_email_to_team_lead")
def send_email_to_team_lead_task(name, email, description):
    logger.info("Email sent successfully")
    return send_email_to_team_lead(name, email, description)