import json
import boto3
import os
import uuid
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Bedrock client with proper settings
region_name = os.environ.get('AWS_REGION', 'us-east-1')
bedrock = boto3.client(
    service_name='bedrock-runtime', 
    region_name=region_name
)

# Initialize S3 client
s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'emaill-generatorcc')

# Model ID - updated to DeepSeek R1 model
MODEL_ID = 'deepseek.r1-v1:0'

def generate_email(purpose, recipient, key_points, tone):
    """Generate email using Amazon Bedrock with DeepSeek R1 model"""
    
    # Prepare the prompt
    prompt = f"""
    You are a professional email assistant. Draft a professional email with the following details:

    Purpose: {purpose}
    Recipient: {recipient}
    Key points: {key_points}
    Tone: {tone}

    Format the email with an appropriate subject line, greeting, body, and closing.
    """
    
    # Prepare request body for DeepSeek model (different format than Claude)
    request_body = {
        "prompt": prompt,
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    try:
        # Invoke the model
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(request_body)
        )
        
        # Parse the response (DeepSeek format is different from Claude)
        response_body = json.loads(response['body'].read().decode('utf-8'))
        generated_email = response_body.get('generation', '')
        
        # Log success (without including full email content)
        logger.info("Email generated successfully")
        
        return {
            'statusCode': 200,
            'email': generated_email
        }
    except Exception as e:
        logger.error(f"Error generating email: {str(e)}")
        return {
            'statusCode': 500,
            'error': str(e)
        }

def save_to_s3(email_data, email_id=None):
    """Save generated email to S3 bucket"""
    if not email_id:
        email_id = str(uuid.uuid4())
    
    try:
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"emails/{email_id}.json",
            Body=json.dumps(email_data),
            ContentType='application/json'
        )
        logger.info(f"Email saved to S3 with ID: {email_id}")
        return email_id
    except Exception as e:
        logger.error(f"Error saving to S3: {str(e)}")
        return None

def lambda_handler(event, context):
    """Main Lambda handler function"""
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Parse input from API Gateway
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)
        
        # Extract parameters
        purpose = body.get('purpose', '')
        recipient = body.get('recipient', '')
        key_points = body.get('key_points', '')
        tone = body.get('tone', 'professional')
        
        # Log the received parameters for debugging
        logger.info(f"Received parameters: purpose={purpose[:20]}..., recipient={recipient[:20]}..., tone={tone}")
        
        # Validate input
        if not purpose or not recipient or not key_points:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameters (purpose, recipient, or key_points)'
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }
        
        # Generate the email
        result = generate_email(purpose, recipient, key_points, tone)
        
        if result['statusCode'] == 200:
            # Save to S3
            email_data = {
                'purpose': purpose,
                'recipient': recipient,
                'key_points': key_points,
                'tone': tone,
                'generated_email': result['email']
            }
            email_id = save_to_s3(email_data)
            
            # Return the result
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'email': result['email'],
                    'email_id': email_id
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }
        else:
            return {
                'statusCode': result['statusCode'],
                'body': json.dumps({
                    'error': result.get('error', 'Error generating email')
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f"Internal server error: {str(e)}"
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
