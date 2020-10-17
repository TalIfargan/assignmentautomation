from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email
from flask_wtf.file import FileField, FileRequired, FileAllowed


class CoverForm(FlaskForm):
    faculties = ('', 'Aerospace Engineering', 'Architecture and Town Planning', 'Biology', 'Biomedical Engineering',
                 'Biotechnology and Food Engineering', 'Chemical Engineering', 'Chemistry',
                 'Civil and Environmental Engineering', 'Computer Science', 'Education in Science and Technology',
                 'Electrical Engineering', 'Industrial Engineering and Management', 'Materials Science & Engineering',
                 'Mathematics', 'Mechanical Engineering', 'Medicine', 'Physics', 'Humanities and Arts')
    course_id = StringField(u'Course ID', validators=[DataRequired()])
    faculty = SelectField(u'Faculty', choices=faculties, validators=[DataRequired()])
    partner_name = StringField(u'Partner Name')
    partner_id = StringField(u'Partner Student Number')
    year = StringField(u'Year', validators=[DataRequired()])
    semester = StringField(u'Semester', validators=[DataRequired()])
    # assignment_number = StringField(u'Assignment Number', validators=[DataRequired()])
    submit = SubmitField(u'Done')


class NewCover(FlaskForm):
    course_name = StringField(u'Course Name', validators=[DataRequired()])
    submit = SubmitField(u'Create New Cover')


class UploadScan(FlaskForm):
    cover = SelectField(u'Choose Cover', validators=[DataRequired()])
    assignment_numbers = (
        ('', ''), ('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
        ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13 - are you kidding?'))
    assignment_number = SelectField(u'Assignment Number', validators=[DataRequired()], choices=assignment_numbers)
    scan = FileField(u'Scan Upload', validators=[FileRequired(), FileAllowed(['pdf'], 'pdf extension file only!')])
    date_of_submission = StringField(validators=[DataRequired()])
    submit = SubmitField(u'Create Submission')


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(message="Please enter your name.")])
    email = StringField("Email", validators=[DataRequired(message="Please enter your email address."),
                                             Email(message="Please enter a valid email address")])
    subject = StringField("Subject", validators=[DataRequired(message="Please enter a subject.")])
    message = TextAreaField("Message", validators=[DataRequired(message="Please enter a message.")])
    submit = SubmitField("Send")


class DownloadPDF(FlaskForm):
    submit = SubmitField("Download Submission")
