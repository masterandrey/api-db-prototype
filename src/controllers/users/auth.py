import db.conn
import db.models
from jwt_token import token, JWT_CREATED, JWT_EXPIRATION
from controllers.helper import transaction, api_result
from controllers.models import JWT_EMAIL, JWT_GROUP, UNAUTH_OPER_CODE, APP_ERROR_CODE
from journaling import log
import passwords
import settings


@api_result
@transaction
def get_token(email: str, password: str):
    """
    Returns JWT for the email/password.
    """
    users = db.conn.session.query(db.models.User).filter(db.models.User.email == email)
    if not users.count():
        log.debug(f'No user with email={email}')
        return f'No user with email={email}', APP_ERROR_CODE
    user = users.first()
    if not passwords.verify(password, user.password_hash):
        log.debug(f'Invalid email/password for user {email}')
        return f'Invalid email/password for user {email}', UNAUTH_OPER_CODE
    log.debug(f'Issuing JWT for {email}')
    payload = {
        JWT_EXPIRATION: token.datetime2jwt(settings.config.now() + settings.config.token_expiration_delta),
        JWT_CREATED: token.datetime2jwt(settings.config.now()),
        JWT_EMAIL: user.email,
        JWT_GROUP: user.group
    }
    assert '.' not in payload['exp']
    return {'token': token.encode(payload)}