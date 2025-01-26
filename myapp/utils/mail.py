import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from jinja2 import Template

def send_email(receiver_email, subject,name, main_content, template_path="myapp/templates/email_template.html"):
    """
    Function to send a personalized email with an HTML template.

    Args:
    sender_email (str): Sender's email address.
    password (str): Sender's email password (or app-specific password).
    receiver_email (str): Recipient's email address.
    subject (str): Subject of the email.
    name (str): Recipient's name.
    main_content (str): Greeting or main content of the email.
    template_path (str): Path to the HTML email template file .

    Returns:
    None
    """
    
    # Load the email template
    if os.path.exists(template_path):
        with open(template_path, "r") as file:
            template_content = file.read()

        # Create the Jinja2 template
        template = Template(template_content)

        # Render the template with dynamic values
        html_content = template.render(subject=subject,name = name,  main_content = main_content)
    else:
        print(f"Template file not found: {template_path}")
        return

    # Construct the email
    msg = MIMEMultipart("alternative")
    msg["From"] = "growthadvisorhub@gmail.com"
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html"))

    # Send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()  # Start TLS encryption
        server.login("growthadvisorhub@gmail.com", "jypatvccevzhujht")

        # Send the email
        server.sendmail("growthadvisorhub@gmail.com", receiver_email, msg.as_string())
        print("Email sent successfully!")

    except smtplib.SMTPAuthenticationError:
        print("Failed to authenticate. Check your email/password.")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")
    finally:
        if 'server' in locals():
            server.quit()

# Example of how to call the function
'''send_email(
    receiver_email="k.styczen222@gmail.com",
    subject="Awesome tool for awesome people!",
    name="Kamil",
    main_content="Thank you for joining us!<p>We are excited to have you on board.",#this is written in html
)'''

