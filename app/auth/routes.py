from flask import render_template, flash, redirect, url_for, request
from app import db
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm, ChangeFullnameForm, ChangePasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
from app.auth.email import send_password_reset_email
from app.auth import bp


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,
                    fullname=form.fullname.data, student_number=form.student_number.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You registered successfully!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@bp.route('/edit_profile/<username>', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    change_fullname = ChangeFullnameForm()
    change_password = ChangePasswordForm()
    if change_fullname.validate_on_submit():
        user.fullname = change_fullname.fullname.data
        db.session.commit()
        flash('Your fullname has been changed.')
        return redirect(url_for('auth.edit_profile', username=user.username))
    if change_password.validate_on_submit():
        user.set_password(change_password.password.data)
        db.session.commit()
        flash('Your password has been changed.')
        return redirect(url_for('auth.edit_profile', username=user.username))
    return render_template('auth/edit_profile.html', user=user,
                           change_fullname=change_fullname, change_password=change_password)
