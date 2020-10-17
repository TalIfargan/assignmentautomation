import errno
import io
import tempfile
import portalocker
import threading
import shutil
import time
from uuid import uuid4
from flask import render_template, flash, redirect, url_for, send_from_directory, current_app, request, \
    after_this_request, send_file
import pdfkit
from app import db
from app.main.forms import CoverForm, NewCover, UploadScan, ContactForm, DownloadPDF
from flask_login import current_user, login_required
from app.models import User, Cover
from app.main import bp
from PyPDF2 import PdfFileMerger
import os
from app.email import send_email


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')


@bp.route('/covers/<username>', methods=['GET', 'POST'])
@login_required
def covers(username):
    user = User.query.filter_by(username=username).first_or_404()
    user_covers = user.covers
    form = NewCover()
    if form.validate_on_submit():
        cover = Cover(course_name=form.course_name.data, author=user)
        db.session.add(cover)
        db.session.commit()
        flash('A new cover successfully created!')
        return redirect(url_for('main.covers', username=current_user.username))
    return render_template('covers.html', form=form, user=user, covers=user_covers)


@bp.route('/delete_cover/<cover_name>')
@login_required
def delete_cover(cover_name):
    cover = current_user.covers.filter_by(course_name=cover_name).first_or_404()
    db.session.delete(cover)
    db.session.commit()
    flash('{} cover deleted'.format(cover.course_name))
    return redirect(url_for('main.covers', username=current_user.username))


@bp.route('/edit_cover/<cover_name>', methods=['GET', 'POST'])
@login_required
def edit_cover(cover_name):
    cover = current_user.covers.filter_by(course_name=cover_name).first_or_404()
    form = CoverForm()
    if form.validate_on_submit():
        cover.course_id = form.course_id.data
        cover.faculty = form.faculty.data
        cover.partner_name = form.partner_name.data
        cover.partner_id = form.partner_id.data
        cover.year = form.year.data
        cover.semester = form.semester.data
        # cover.assignment_number = form.assignment_number.data
        db.session.commit()
        flash('Your cover successfully edited!')
    return render_template('edit_cover.html', cover=cover, form=form)


@bp.route('/create_cover/<cover_name>', methods=['GET', 'POST'])
@login_required
def create_cover(cover_name):
    user = current_user
    cover = user.covers.filter_by(course_name=cover_name).first_or_404()
    return render_template('create_cover.html', cover=cover, user=user)


@bp.route('/prepare_submission', methods=['GET', 'POST'])
@login_required
def prepare_submission():
    form = UploadScan()
    user = current_user
    cover = user.covers.filter_by(course_name=form.cover.data).first()
    user_covers = current_user.covers
    form.cover.choices = [cover.course_name for cover in user_covers]
    if form.validate_on_submit():
        cover.assignment_number = form.assignment_number.data
        cover.submission_date = form.date_of_submission.data
        html_cover = render_template('create_cover.html', cover=cover, user=user)
        config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files (x86)\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        options = {
            "enable-local-file-access": None
        }
        pdf_cover = pdfkit.from_string(html_cover, False, configuration=config, options=options)
        uploaded_scan = form.scan.data
        pdf_content = io.BytesIO(uploaded_scan.read())
        cover_content = io.BytesIO(pdf_cover)
        upload_key = concat_pdfs(cover, cover_content, pdf_content)
        if upload_key != "Failure":
            flash('You are now welcome to download your submission, Good Luck!')
            return redirect(url_for('main.download_pdf', upload_key=upload_key))
        else:
            flash("Couldn't upload file, please contact the site administrator")
    return render_template('prepare_submission.html', form=form)


def concat_pdfs(cover, cover_content, scan):
    # upload_key = str(uuid4())
    target = os.path.join(current_app.root_path, 'static', 'temp')
    tempdir = tempfile.mkdtemp(dir=target)
    os.chdir(tempdir)
    merger = PdfFileMerger()
    merger.append(cover_content)
    merger.append(scan)
    merger.write('{} - assignment number {}.pdf'.format(cover.course_name, cover.assignment_number))
    merger.close()
    return os.path.basename(tempdir)


@bp.route('/download_pdf/<upload_key>', methods=['GET', 'POST'])
@login_required
def download_pdf(upload_key):
    form = DownloadPDF()
    current_app.temp_lock.acquire()
    if form.validate_on_submit():
        return redirect(url_for('main.pdf_as_attachment', upload_key=upload_key))
    os.chdir(current_app.root_path)
    current_app.temp_lock.release()
    return render_template('download_pdf.html', upload_key=upload_key, form=form)


@bp.route('/pdf_as_attachment/<upload_key>')
@login_required
def pdf_as_attachment(upload_key):
    path = os.path.join(current_app.root_path, 'static', 'temp', upload_key)
    files = [x.path for x in os.scandir(path) if x.is_file()]
    pdf_file = os.path.basename(files[0])
    return send_from_directory(path, pdf_file, as_attachment=True)


@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            send_email(subject=form.subject.data, sender=current_app.config['ADMINS'][0],
                       recipients=[current_app.config['ADMINS'][0]],
                       text_body=render_template('email/contact.txt', form=form),
                       html_body=render_template('email/contact.html', form=form))
            return render_template('contact.html', success=True)
        else:
            flash('All fields are required.')
            return render_template('contact.html', form=form)
    elif request.method == 'GET':
        return render_template('contact.html', form=form)
