"""
EleKnowledge Signup Lambda Function
Cognito User Pool Integration
"""
import json
import logging
import os
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def _parse_request_body(event, required_fields, optional_fields=()):
    """JSON オブジェクト本文と認証項目の文字列型を検証する。"""
    raw_body = event.get('body')
    if isinstance(raw_body, str):
        try:
            body = json.loads(raw_body)
        except (json.JSONDecodeError, RecursionError):
            logger.warning(json.dumps({
                'event': 'auth_request_validation_failed',
                'reason': 'invalid_json'
            }))
            return None
    elif isinstance(raw_body, dict):
        body = raw_body
    elif raw_body is None:
        body = {}
    else:
        body = None

    if not isinstance(body, dict):
        logger.warning(json.dumps({
            'event': 'auth_request_validation_failed',
            'reason': 'body_must_be_object'
        }))
        return None

    invalid_required = any(
        not isinstance(body.get(field), str) or not body.get(field)
        for field in required_fields
    )
    invalid_optional = any(
        field in body and not isinstance(body[field], str)
        for field in optional_fields
    )
    if invalid_required or invalid_optional:
        logger.warning(json.dumps({
            'event': 'auth_request_validation_failed',
            'reason': 'invalid_field_type_or_missing_field'
        }))
        return None
    return body


def _validation_error(headers):
    return {
        'statusCode': 400,
        'headers': headers,
        'body': json.dumps({
            'error': 'ValidationError',
            'message': 'Request body is invalid'
        })
    }

# Initialize AWS clients
cognito_client = boto3.client('cognito-idp')
dynamodb = boto3.resource('dynamodb')

# Environment variables
USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID')
CLIENT_ID = os.environ.get('COGNITO_CLIENT_ID')
USERS_TABLE_NAME = os.environ.get('USERS_TABLE')

# DynamoDB table
users_table = dynamodb.Table(USERS_TABLE_NAME)


def lambda_handler(event, context):
    """
    Handle user signup
    
    Expected event body:
    {
        "email": "user@example.com",
        "password": "SecurePassword123!",
        "name": "User Name" (optional)
    }
    """
    
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
    }
    
    try:
        body = _parse_request_body(event, ('email', 'password'), ('name',))
        if body is None:
            return _validation_error(headers)
        
        email = body.get('email')
        password = body.get('password')
        name = body.get('name', '')
        
        # Create user in Cognito
        user_attributes = [
            {'Name': 'email', 'Value': email}
        ]
        
        if name:
            user_attributes.append({'Name': 'name', 'Value': name})
        
        cognito_response = cognito_client.sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=user_attributes
        )
        
        user_sub = cognito_response['UserSub']
        
        # Store user info in DynamoDB
        users_table.put_item(
            Item={
                'userId': user_sub,
                'email': email,
                'username': name if name else email.split('@')[0],
                'createdAt': context.request_time_epoch if hasattr(context, 'request_time_epoch') else None,
                'role': 'user'
            }
        )
        
        return {
            'statusCode': 201,
            'headers': headers,
            'body': json.dumps({
                'message': 'User registered successfully. Please check your email for verification code.',
                'userId': user_sub,
                'email': email
            })
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        # Handle specific Cognito errors
        if error_code == 'UsernameExistsException':
            return {
                'statusCode': 409,
                'headers': headers,
                'body': json.dumps({
                    'error': 'UserExistsError',
                    'message': 'An account with this email already exists'
                })
            }
        elif error_code == 'InvalidPasswordException':
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'InvalidPasswordError',
                    'message': 'Password does not meet requirements: 8+ characters, uppercase, lowercase, number, symbol'
                })
            }
        else:
            logger.error(json.dumps({
                'event': 'auth_cognito_error',
                'error_code': error_code
            }))
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({
                    'error': 'InternalServerError',
                    'message': 'An unexpected error occurred'
                })
            }
    
    except Exception as e:
        logger.error(json.dumps({
            'event': 'auth_unexpected_error',
            'error_type': type(e).__name__
        }))
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'InternalServerError',
                'message': 'An unexpected error occurred'
            })
        }
