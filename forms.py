from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email= StringField('Email',
                       validators=[DataRequired(), Email()])
    password= PasswordField('Password', validators=[DataRequired()])
    confirm_password= PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit= SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email',
                       validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log in')

class CommentForm(FlaskForm):
    text = TextAreaField('Your Comment', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField ('Post Comment')






