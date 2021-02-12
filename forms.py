from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, EqualTo
from wtforms import StringField, PasswordField, SubmitField, SelectField, HiddenField


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=18)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=18)])
    nation = SelectField('Nation', choices=[("earth", "Earth Kingdom"), ("water", "Watar Tribe"),
                                            ("fire", "Fire Nation"), ("air", "Air Nomads")],
                         validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class QuestionForm(FlaskForm):
    question_id = HiddenField()
    answer = StringField('Write your answer here:', validators=[DataRequired()])
    submit = SubmitField("Submit")
