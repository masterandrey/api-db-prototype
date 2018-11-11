import db.conn
import db.models
from controllers.models import NewUser


def create_user(new_user: NewUser):
    """
    Creates user.
    Returns new user id.
    """
    try:
        # todo: check uniq name, email?
        if not isinstance(new_user, dict):
            new_user = new_user.as_dict
        print(f'Creating user {new_user}')
        users = db.conn.session.query(db.models.User).filter(db.models.User.name == new_user['name'])
        if users.count():
            db.conn.session.close()
            return f'User with name="{new_user["name"]}" already exists', 400
        users = db.conn.session.query(db.models.User).filter(db.models.User.email == new_user['email'])
        if users.count():
            db.conn.session.close()
            return f'User with email="{new_user["email"]}" already exists', 400
        db_user = db.models.User(**new_user)
        db.conn.session.add(db_user)
        db.conn.session.commit()
        return {
            'result': {'id': db_user.id},
            'success': True
        }
    except Exception as e:
        db.conn.session.rollback()
        return f'{e}', 400  #todo: internal exception only to log