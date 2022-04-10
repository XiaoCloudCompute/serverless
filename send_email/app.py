import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('track')
    message = event['Records'][0]['Sns']['Message']
    email_data = json.loads(message)
    print(email_data)

    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "Account <account@prod.huanlinxiao.me>"
    
    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = email_data['username']

    try:
        response = table.get_item(Key={'username': RECIPIENT})
    except ClientError as e:
        pass
    else:
        return {"status": "duplicate"}
    
    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"
    
    # The subject line for the email.
    SUBJECT = "Account verify email"

    address = f"{email_data['domain']}/v1/verifyUserEmail?" + f"email={email_data['username']}&token={email_data['token']}"
    
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = f"""
    Hi {RECIPIENT},
    You can verify your email by click {address}
    If you have any problem, please contact me
    Best,
    Huanlin Xiao
    """
    
    # The HTML body of the email.
    BODY_HTML = f"""
    <html>
        <head></head>
        <body>
            <h1>Account verify email</h1>
            <p>Hi {RECIPIENT},</p>
            <p>You can verify your email by click
                <a href='{address}'>this</a>
            </p>
            <p>If you have any problem, please contact me</p>
            <p>Best,</p>
            <p>Huanlin Xiao</p>
        </body>
    </html>
    """            
    # The character encoding for the email.
    CHARSET = "UTF-8"
    
    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)
    
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
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
            Source=SENDER,
        )
        response = table.put_item(
            Item={
                'username': RECIPIENT,
            }
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
    return {"status": "OK"}
