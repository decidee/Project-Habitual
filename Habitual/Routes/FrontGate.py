import os
from plistlib import UID
from dotenv import load_dotenv
from flask import render_template, redirect, url_for, request, Blueprint, session, flash
from flask_login import login_user,current_user,logout_user, login_required

from ..Forms.forms import RegisterationForm, LoginForm, TeleForm, TeleFormConfirmationCode
from ..Models.Users_Model import User, Tele
from ..ext import db, bcrypt
import requests

FrontG = Blueprint('FrontG',__name__,url_prefix='/')

env_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
load_dotenv(f"{env_dir}/.env")
request_url = os.getenv('API_URL')


@FrontG.route("/", methods=["GET"])
def index():
    return render_template('index.html')


@FrontG.route("/registration", methods=["GET", "POST"])
def registration():
    form = RegisterationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            password_confirmation = form.password_confirmation.data
            phonenumber = form.phonenumber.data
            Invites = form.Invite.data       
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            db_add = User(UserName=username,PhoneNumber=phonenumber,Password=hashed_password,InviteCode=Invites)
            db.session.add(db_add)
            db.session.commit()        
            
            flash('Registration Successful', 'success')

            return redirect(url_for('FrontG.login'))
        else: flash('Something Went Wrong Please Try Again!', category='danger')
    return render_template('Registration.html', title='Registeration', form=form) 


@FrontG.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(PhoneNumber=form.phonenumber.data).first()
        if user and bcrypt.check_password_hash(user.Password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Login Successful", category='info')
            return redirect(url_for('FrontG.home'))
        else: flash('Incorrect Login, Please try again.', category='danger')
    return render_template('Login.html', title='Login', form=form)


@FrontG.route("/home")
@login_required
def home():
    return render_template('home.html')


@FrontG.route("/telegramreg", methods=["GET", "POST"])
def telegramreg():
    form = TeleForm()
    if form.validate_on_submit():
        api_id = form.Api_Id.data
        api_hash = form.Api_Hash.data
        db_add = Tele(ApiId=api_id,ApiHash=api_hash,OwnerAcc=current_user.id)
        db.session.add(db_add)
        db.session.commit()
        return redirect(url_for('FrontG.SignInCodeReq'))
    return render_template('ApiForm.html', title='Telegram Login', form=form)


@FrontG.route('/SignInCodeReq', methods=['GET','POST'])
@login_required                                                                                            
def SignInCode():
    form = TeleFormConfirmationCode()
    if form.validate_on_submit():
        code = form.TelegramSignInCode.data
        SignInC = {"UserID": current_user.id, "SignInCode":int(code)}
        send_req = requests.post(f"{request_url}/SignInCode", json=SignInC)
    
    return render_template('ApiForm.html', form=form)


@FrontG.route('/logout')
def logout():
    logout_user()
    flash("Logged out")
    return redirect(url_for('FrontG.login'))



