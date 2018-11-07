import models
import db
from flask import abort
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify
import json


def user_list() -> str:
    """
    Users list
    """
    users = db.session.query(models.User)
    return json.dumps([(row.as_dict()) for row in users])
    #return jsonify([user.as_dict() for user in users.all()])
