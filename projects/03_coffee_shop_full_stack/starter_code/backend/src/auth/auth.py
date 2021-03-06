import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'bjb.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@DONE implement get_token_auth_header() method
    DONE it should attempt to get the header from the request
    DONE it should raise an AuthError if no header is present
    DONE it should attempt to split bearer and the token
    DONE it should raise an AuthError if the header is malformed
    DONE return the token part of the header
'''
def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None)
    # If no Authorization header exists, throw 401
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)
    parts = auth.split()
    # If Authorization header is not a bearer token, throw 401
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)
    # If Authorization header does not contain 2 parts, throw 401
    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)
    # If Authorization header has more than 2 parts, throw 401
    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)
    token = parts[1]
    return token # return the token

'''
@DONE implement check_permissions(permission, payload) method
    @INPUTS
        DONE permission: string permission (i.e. 'post:drink')
        DONE payload: decoded jwt payload

    DONE it should raise an AuthError if permissions are not included in the payload
    DONE check your RBAC settings in Auth0
    DONE it should raise an AuthError if the requested permission string is not in the payload permissions array
    DONE return true otherwise
'''
def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'no_permissions',
            'description': 'No permissions component to payload.'
        }, 401)
        # abort(400) # No permissions component to payload
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'insufficient_permissions',
            'description': 'User does not have permissions to take that action.'
        }, 401)
        # abort(403) # We know who you are, but you are denied
    return True  

'''
@DONE implement verify_decode_jwt(token) method
    @INPUTS
        DONE token: a json web token (string)

    DONE it should be an Auth0 token with key id (kid)
    DONE it should verify the token using Auth0 /.well-known/jwks.json
    DONE it should decode the payload from the token
    DONE it should validate the claims
    DONE return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 401)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 401)

'''
@DONE implement @requires_auth(permission) decorator method
    @INPUTS
        DONE permission: string permission (i.e. 'post:drink')

    DONE it should use the get_token_auth_header method to get the token
    DONE it should use the verify_decode_jwt method to decode the jwt
    DONE it should use the check_permissions method validate claims and check the requested permission
    DONE return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator