import os, logging
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from flask import flash, current_app, render_template

def send_mime_email(recipients, text_body, image_file, html_body):
    SENDER = current_app.config['MAIL_USERNAME']
    current_app.logger.setLevel(logging.INFO)
    current_app.logger.info('Sending MIME email')
    RECIPIENT = recipients

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"

    SUBJECT = "You Rack Discipline"
    BODY_TEXT = text_body
    BODY_HTML = html_body

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=AWS_REGION)

    # The full path to the file that will be attached to the email.
    ATTACHMENT = os.path.join(current_app.config['UPLOAD_FOLDER'], image_file)

    # Create a multipart/mixed parent container.
    msg = MIMEMultipart('mixed')
    # Add subject, from and to lines.
    msg['Subject'] = SUBJECT
    msg['From'] = SENDER
    msg['To'] = ', '.join(recipients)

    # Encode the text and HTML content and set the character encoding. This step is
    # necessary if you're sending a message with characters outside the ASCII range.
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgAlternative.attach(textpart)
    msgAlternative.attach(htmlpart)
    # Attach the multipart/alternative child container to the multipart/mixed parent container.
    msg.attach(msgAlternative)

    # Define the attachment part and encode it using MIMEImage.
    try:
        fp = open(ATTACHMENT, 'rb')
        att = MIMEImage(fp.read())
        fp.close()
        # Add a header to tell the email client to treat this part as an attachment,
        # and to give the attachment a name.
        att.add_header('Content-ID', image_file)
        # Add the attachment to the parent container.
        msg.attach(att)
    except IOError as e:
        flash('Looks like the file is missing!')
        flash(e)

    try:
        #Provide the contents of the email.
        response = client.send_raw_email(
            Source=SENDER,
            Destinations=RECIPIENT,
            RawMessage={
                'Data':msg.as_string(),
            },
        )

    except ClientError as e:
        flash(e.response['Error']['Message'])
        current_app.logger.setLevel(logging.ERROR)
        current_app.logger.info('Error sending email:', e.response['Error']['Code'])
        current_app.logger.info('                   :', e.response['Error']['Message'])
        current_app.logger.info('                   :', e.response['Error']['Type'])
    else:
        flash("Email sent! Message ID:" + response['MessageId'])

    return

def send_image_email(recipients, text_body, html_body):
    SENDER = current_app.config['MAIL_USERNAME']
    current_app.logger.setLevel(logging.INFO)
    current_app.logger.info('Sending inline email')
    RECIPIENT = recipients

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"

    SUBJECT = "You Rack Discipline Too"
    BODY_TEXT = text_body
    BODY_HTML = html_body

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=AWS_REGION)

    try:
        #Provide the contents of the email.
        response = client.send_email(
            Source=SENDER,
            Destination={
                'ToAddresses': RECIPIENT
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        flash(e.response['Error']['Message'])
        current_app.logger.setLevel(logging.ERROR)
        current_app.logger.info('Error sending email:', e.response['Error']['Code'])
        current_app.logger.info('                   :', e.response['Error']['Message'])
        current_app.logger.info('                   :', e.response['Error']['Type'])
    else:
        flash("Email sent! Message ID:" + response['MessageId'])

    return

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    SENDER = "yourackdiscipline@gmail.com"
    current_app.logger.setLevel(logging.INFO)
    current_app.logger.info('Sending password reset email')

    RECIPIENT = user.Email

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"

    # The subject line for the email.
    SUBJECT = "You Rack Discipline Password Reset"
    BODY_TEXT = render_template('email/reset_password.txt', user=user, token=token)
    BODY_HTML = render_template('email/reset_password.html', user=user, token=token)

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=AWS_REGION)

    try:
        # Provide the contents of the email.
        response = client.send_email(
            Source=SENDER,
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        current_app.logger.setLevel(logging.ERROR)
        current_app.logger.info('Error sending email:', e.response['Error']['Code'])
        current_app.logger.info('                   :', e.response['Error']['Message'])
        current_app.logger.info('                   :', e.response['Error']['Type'])

    return

