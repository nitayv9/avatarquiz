import random
import os
from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect
from forms import LoginForm, RegisterForm, QuestionForm
from levinstein import levenshteinDistance
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')


            
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

reset_db()

@login_manager.user_loader
def load_user(username):
    return User.query.get(str(username))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(150), nullable=False)
    nation = db.Column(db.String(), nullable=False)
    corrects = db.relationship('Correct', backref="user", lazy=True)

    def get_score(self):
        all_corrects = Correct.query.filter_by(user_id=self.id).all()
        return sum(correct.question.score for correct in all_corrects)


class Question(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    content = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    picture = db.Column(db.String(150), nullable=False, default='default.png')
    answers = db.relationship('Answer', backref="question", lazy=True)
    corrects = db.relationship('Correct', backref="question", lazy=True)


class Answer(db.Model):
    answer_id = db.Column(db.Integer(), primary_key=True)
    question_id = db.Column(db.Integer(), db.ForeignKey('question.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)


class Correct(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer(), db.ForeignKey('question.id'), nullable=False)
    date_answered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"""Correct({self.id}, {self.user_id}, {self.question_id}, {self.date_answered})"""

    def __str__(self):
        return f"""Correct({self.id}, {self.user_id}, {self.question_id}, {self.date_answered})"""


def insert_question(content, score, picture, *answers):
    new_question = Question(content=content, score=score, picture=picture)
    db.session.add(new_question)
    db.session.commit()
    new_id = new_question.id
    for answer in answers:
        db.session.add(Answer(question_id=new_id, content=answer))
    db.session.commit()


def get_score(user):
    all_corrects = Correct.query.filter_by(user_id=user.id).all()
    return sum(correct.question.score for correct in all_corrects)


@app.route("/")
def home():

    return render_template("home.j2", title="Home")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("Cant get to the login page. Already logged in")
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f"Welcome Back {form.username.data}!")
            return redirect(url_for('home'))
        else:
            flash("unsuccessful login, Check again the username and password")
    return render_template("login.j2", form=form, title="Login")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash("Cant get to the register page. Already logged in")
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash(f"{form.username.data} is already exist. try another username")
            return redirect(url_for('register'))
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_password, nation=form.nation.data)
        db.session.add(new_user)
        db.session.commit()
        flash(f"{form.username.data} has been registered succesfully, Wellcome to Avatar Quiz!")
        return redirect(url_for('login'))
    return render_template("register.j2", form=form, title="Register")


@app.route("/quiz", methods=['GET', 'POST'])
def quiz():
    if current_user.is_authenticated:
        form = QuestionForm()
        if form.validate_on_submit():
            question = Question.query.get(form.question_id.data)
            answers = [answer.content.lower().replace(' ', '') for answer in question.answers]
            input_answer = form.answer.data.lower().replace(' ', '')
            check = [levenshteinDistance(input_answer, answer) < 3 for answer in answers]
            if True in check:
                db.session.add(Correct(user_id=current_user.id, question_id=question.id))
                db.session.commit()
                flash("Correct Answer")
            else:
                flash("Wrong Answer")
        all_questions = set(Question.query.all())
        answered_already = {correct.question for correct in Correct.query.filter_by(user_id=current_user.id).all()}
        unanswered = all_questions.difference(answered_already)
        if len(unanswered) == 0:
            flash("Well Done!! You have already answered all the questions we have")
            return redirect(url_for('home'))
        question = random.choice(list(unanswered))
        number = question.id
        form.question_id.process_data(number)
        return render_template("quiz.j2", question=question, form=form, title=f"quiz - {number}")
    else:
        flash("Cant play without login")
        return redirect(url_for('login'))


@app.route('/board')
def board():
    all_users = User.query.all()
    all_users.sort(key=get_score, reverse=True)
    all_users = all_users[:10]
    return render_template("board.j2", all_users=all_users)

@app.route('/profile')
def profile():
    if current_user.is_authenticated:
        num_of_corrects = len(current_user.corrects)
        all_questions = Question.query.all()
        answered = current_user.corrects
        num_of_remain = len(Question.query.all()) - len(current_user.corrects)

        return render_template('profile.j2', num_of_corrects=num_of_corrects, remain=num_of_remain)
    else:
        flash("Cant get to your profile without login")
        return redirect(url_for('login'))

@app.route('/credit')
def credit():
    return render_template('credit.j2')


if __name__ == '__main__':
    app.run()
