"""
Encapsulates SQLAlchemy engine, session and db management logic
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base
from sqlalchemy.orm import Session, scoped_session
from journaling import log
import settings
import db.models
import controllers.models
import settings


session: Session = None


def create_admin_user():
    """
    Creates default admin if no users with admin right are in DB
    """
    # if session.info.get('has_flushed', False):
    users = db.models.User.query().filter(db.models.User.group == controllers.models.ADMIN_ACCESS_GROUP)
    if not users.count():
        log.debug('!' * 25 + f"""
Creating default admin user <{settings.config.default_admin_email}> with
password '{settings.config.default_admin_password}' - please change her password
""" + '!' * 25)
        admin_user = db.models.User(
            email=settings.config.default_admin_email,
            password=settings.config.default_admin_password,
            group=controllers.models.ADMIN_ACCESS_GROUP
        )
        session.add(admin_user)
        session.commit()
    else:
        log.debug(f'In db found users with admin roles: {", ".join([user.email for user in users])}')


def make_session():
    global session
    log.debug(f'...Connecting to DB {settings.config.db_uri}...')
    engine = create_engine(
        settings.config.db_uri,
        echo=settings.config.db_sqltrace
    )

    session = scoped_session(sessionmaker(bind=engine))  # ()
    Base.metadata.bind = engine
    if settings.config.db_autometa:
        refresh_metadata()
    create_admin_user()
    return session


def refresh_metadata():
    log.debug('Refreshing metadata...')
    Base.metadata.create_all(session.get_bind())
    session.commit()
