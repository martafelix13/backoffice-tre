import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_project_status_email(user_email, project_name, status, feedback=None):
    sender_email = "youremail@example.com"
    sender_password = "yourpassword"

    subject = f"Status update on your project: {project_name}"

    if status == "A-E":
        body = (
            f"Dear User,\n\n"
            f"We're happy to let you know that your project *{project_name}* has been approved! 🎉\n"
            f"You can now sign the Data Processing Agreement regarding your data.\n\n"
            f"Thank you for your submission, and let us know if you have any questions.\n\n"
            f"Best regards,\n"
            f"The Adele Team"
        )

    elif status == "P-R":
        body = (
            f"Dear User,\n\n"
            f"Unfortunately, your project *{project_name}* was not approved for TRE Adele.\n\n"
            f"Here's some feedback to help you revise your submission:\n"
            f"{feedback}\n\n"
            f"We encourage you to address the points above and try again. We're here to support you!\n\n"
            f"Warm regards,\n"
            f"The Adele Team"
        )

    elif status == "A-R":
        body = (
            f"Dear User,\n\n"
            f"Good news! The Data Processing Agreement (DPA) for your project *{project_name}* has been approved. ✅\n"
            f"{'Here’s a note from the reviewer: ' + feedback if feedback else ''}\n\n"
            f"Now you can submit your metadata through our forms to improve findability and upload your data following our guide.\n\n"
            f"Thanks for your effort and collaboration.\n\n"
            f"Best,\n"
            f"The Adele Team"
        )

    elif status == "M-E":
        body = (
            f"Dear User,\n\n"
            f"Unfortunately, the Data Processing Agreement (DPA) for your project *{project_name}* could not be approved at this time.\n\n"
            f"The reason provided was:\n"
            f"{feedback}\n\n"
            f"Please review the feedback and resubmit when ready—we’re here to help.\n\n"
            f"Kind regards,\n"
            f"The Adele Team"
        )

        
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = user_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, user_email, message.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
