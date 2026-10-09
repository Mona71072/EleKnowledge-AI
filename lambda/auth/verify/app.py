"""
EleKnowledge Email Verification Lambda Function
Cognito Email Confirmation
"""
import json
import logging
import os
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def _parse_request_body(event, required_fields):
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
    if invalid_required:
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

# Environment variables
USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID')
CLIENT_ID = os.environ.get('COGNITO_CLIENT_ID')


def lambda_handler(event, context):
    """
    Handle email verification
    
    Expected event body:
    {
        "email": "user@example.com",
        "code": "123456"
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
        body = _parse_request_body(event, ('email', 'code'))
        if body is None:
            return _validation_error(headers)
        
        email = body.get('email')
        code = body.get('code')
        
        # Confirm signup with verification code
        cognito_client.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            ConfirmationCode=code
        )
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Email verified successfully. You can now log in.',
                'email': email
            })
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        # Handle specific Cognito errors
        if error_code == 'CodeMismatchException':
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'InvalidCodeError',
                    'message': 'Invalid verification code'
                })
            }
        elif error_code == 'ExpiredCodeException':
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'ExpiredCodeError',
                    'message': 'Verification code has expired. Please request a new code.'
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
        elif error_code == 'NotAuthorizedException':
            return {
                'statusCode': 403,
                'headers': headers,
                'body': json.dumps({
                    'error': 'AlreadyConfirmedError',
                    'message': 'User is already confirmed'
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
