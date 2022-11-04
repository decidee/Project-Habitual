from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from ..Models.Users_Model import User, Tele, Invites


class RegisterationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),Length(min=5, max=15, message="Username Must be between %(min)d - %(max)d"  )])
    password = PasswordField('Password', validators=[DataRequired(),Length(max=40)])
    password_confirmation = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords dosen\'t match')])
    phonenumber = StringField('Phone Number', validators=[DataRequired()])
    Invite = StringField('Invite Code', validators=[DataRequired()])
 
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        user_check = User.query.filter_by(UserName=username.data).first()
        if user_check:
            raise ValidationError('Username Already Taken.')

    def validate_phonenumber(self,phonenumber):
        phone_check = User.query.filter_by(PhoneNumber=phonenumber.data).first()
        if phone_check:
            raise ValidationError('Phone Number exists.')


    def validate_Invite(self,Invite):
        Invite_check = Invites.query.filter_by(InviteWords=Invite.data).first()
        Invite_Input = User.query.filter_by(InviteCode=Invite.data).first()
        if Invite_Input or Invite_check == None:
            raise ValidationError('Invalied Invite Code.')



class LoginForm(FlaskForm):
    phonenumber = StringField('Phone Number', validators=[DataRequired(message="Please Input your Phone Number")])
    password = PasswordField('Password', validators=[DataRequired(message="Please Input your Password")])
    remember = BooleanField('Remember Me')
    
    submit = SubmitField('Login')


class TeleForm(FlaskForm):
    Api_Id = StringField('Api ID', validators=[DataRequired()])
    Api_Hash = StringField('Api Hash', validators=[DataRequired()])