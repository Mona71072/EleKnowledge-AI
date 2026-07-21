"""Cognito PreSignUp / PreAuthentication trigger.

Allows only email addresses in:
  - @meltec.co.jp                         (exact domain)
  - @<subdomain>.mitsubishielectric.co.jp (any single-or-multi-label subdomain)

Rejects everything else by raising an exception, which Cognito surfaces to the
client as a sign-up / sign-in error.
"""
import re

ALLOWED = re.compile(
    r'^[^@]+@('
    r'meltec\.co\.jp'
    r'|[A-Za-z0-9][A-Za-z0-9.-]*\.mitsubishielectric\.co\.jp'
    r')$',
    re.IGNORECASE,
)

MSG = ("Email domain not allowed. Only @meltec.co.jp or "
       "@*.mitsubishielectric.co.jp addresses may register or sign in.")


def handler(event, context):
    attrs = (event.get('request') or {}).get('userAttributes') or {}
    email = (attrs.get('email') or '').strip()
    if not ALLOWED.match(email):
        # message is returned to the client by Cognito
        raise Exception(MSG)
    return event
