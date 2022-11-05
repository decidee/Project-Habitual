from enum import unique
import uuid
from datetime import datetime
import pytz
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID
from ..ext import db,login_manager


@login_manager.user_loader
def user_loader(user_id):
    user_search = User.query.get(user_id)
    if user_search:
        user = User()
        user.id = user_id
        user.name = user_search.UserName
        return user
    # return User.query.get(user_id)



'''
@login_manager.request_loader
def request_loader(request):
    user_id = request.form.get('UID')
    if user_id not in users:
        return

    user = User()
    user.id = user_id
    return user

'''


class User(db.Model,UserMixin):
    __tablename__ = "UserAcc"
    UID = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    UserName = db.Column(db.String(20), unique = True, nullable=False)
    PhoneNumber = db.Column(db.String(20), unique = True, nullable=False)
    Password = db.Column(db.String(128), nullable=False)
    CreatedOn = db.Column(db.DateTime(), default=datetime.now(pytz.utc))
    InviteCode = db.Column(db.String(30), nullable=False)
    LinkAcc = db.relationship('Tele', backref='UserAcc')
    
    def get_id(self):
            return str(self.UID)


class Tele(db.Model):
    __tablename__ = "TeleAcc"
    id = db.Column(db.Integer,primary_key=True)
    ApiId = db.Column(db.String(50))
    ApiHash = db.Column(db.String(128))
    OwnerAcc = db.Column(db.ForeignKey('UserAcc.UID'),unique=True)
    SessionFile = db.Column(db.String(2000), nullable=True)


class Invites(db.Model):
    __tablename__ = "Invites"
    id = db.Column(db.Integer,primary_key=True)
    InviteWords = db.Column(db.String(30), nullable=False)