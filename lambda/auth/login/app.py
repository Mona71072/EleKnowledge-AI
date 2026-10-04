"""
EleKnowledge Login Lambda Function
Cognito User Pool Authentication
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
    Handle user login
    
    Expected event body:
    {
        "email": "user@example.com",
        "password": "SecurePassword123!"
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
        body = _parse_request_body(event, ('email', 'password'))
        if body is None:
            return _validation_error(headers)
        
        email = body.get('email')
        password = body.get('password')
        
        # Authenticate with Cognito
        auth_response = cognito_client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )
        
        # Get user attributes from Cognito
        user_response = cognito_client.get_user(
            AccessToken=auth_response['AuthenticationResult']['AccessToken']
        )
        
        user_sub = user_response['Username']
        
        # Update last login time in DynamoDB
        try:
            import time
            users_table.update_item(
                Key={'userId': user_sub},
                UpdateExpression='SET lastLoginAt = :timestamp',
                ExpressionAttributeValues={
                    ':timestamp': int(time.time())
                }
            )
        except Exception as update_error:
            logger.error(json.dumps({
                'event': 'auth_last_login_update_failed',
                'error_type': type(update_error).__name__
            }))
        
        # Return tokens and user info
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Login successful',
                'tokens': {
                    'accessToken': auth_response['AuthenticationResult']['AccessToken'],
                    'idToken': auth_response['AuthenticationResult']['IdToken'],
                    'refreshToken': auth_response['AuthenticationResult']['RefreshToken'],
                    'expiresIn': auth_response['AuthenticationResult']['ExpiresIn']
                },
                'user': {
                    'userId': user_sub,
                    'email': email
                }
            })
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        # Handle specific Cognito errors
        if error_code == 'NotAuthorizedException':
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({
                    'error': 'AuthenticationError',
                    'message': 'Incorrect email or password'
                })
            }
        elif error_code == 'UserNotFoundException':
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({
                    'error': 'UserNotFoundError',
                    'message': 'User account does not exist'
                })
            }
        elif error_code == 'UserNotConfirmedException':
            return {
                'statusCode': 403,
                'headers': headers,
                'body': json.dumps({
                    'error': 'UserNotConfirmedError',
                    'message': 'Please verify your email before logging in'
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
