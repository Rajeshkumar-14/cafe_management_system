from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from celery import shared_task

__project_by__ = "RajeshKumar"


def send_welcome_email(user_email):
    subject = "Welcome to Our Website"
    html_message = render_to_string(
        "email/welcome-email.html", {"user_email": user_email}
    )
    plain_message = strip_tags(html_message)
    from_email = "noreply@example.com"
    recipient_list = [user_email]

    send_mail(
        subject, plain_message, from_email, recipient_list, html_message=html_message
    )
    print("Registration mail sent")


def send_password_reset(user_id):
    user = User.objects.get(pk=user_id)
    token_generator = PasswordResetTokenGenerator()
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

    subject = "Password Reset"
    token = token_generator.make_token(user)
    reset_link = f"http://127.0.0.1:8000/auth/password_reset_confirm/{uidb64}/{token}/"

    html_message = render_to_string(
        "email/password-reset-mail.html", {"reset_link": reset_link}
    )
    from_email = "noreply@example.com"
    plain_message = strip_tags(html_message)
    user_email = user.email
    recipient_list = [user_email]
    send_mail(
        subject, plain_message, from_email, recipient_list, html_message=html_message
    )

    print("Password reset email successfully sent")


def password_change_alert(user_email):
    subject = "Password Changed Successfully"
    html_message = render_to_string("email/password-reset-success.html")
    plain_message = strip_tags(html_message)
    from_email = "noreply@example.com"
    recipient_list = [user_email]
    send_mail(
        subject, plain_message, from_email, recipient_list, html_message=html_message
    )
    print("Password change alert successfully sent to", user_email)
