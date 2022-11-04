from plistlib import UID
from flask import render_template, redirect, url_for, request, Blueprint, session, flash
from flask_login import login_user,current_user,logout_user, login_required

from ..Forms.forms import RegisterationForm, LoginForm
from ..Models.Users_Model import Invites, User
from ..ext import db, bcrypt
from ..Invite_gen import generate_word

FrontG = Blueprint('FrontG',__name__,url_prefix='/')


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
    q = print(current_user)
    return render_template('home.html')

@FrontG.route("/telegramreg")
def telegramreg():
    return "<H1>Telegram Registration<H1>"


@FrontG.route('/logout')
def logout():
    # session.pop('username', None)
    logout_user()
    flash("Logged out")
    return redirect(url_for('FrontG.login'))