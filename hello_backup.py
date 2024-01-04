from flask import Flask, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, equal_to, ValidationError, length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin, current_user
from sqlalchemy import MetaData


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
metadata = MetaData(
    naming_convention={
        'pk': 'pk_%(table_name)s',
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        'ix': 'ix_%(table_name)s_%(column_0_name)s',
        'uq': 'uq_%(table_name)s_%(column_0_name)s',
        'ck': 'ck_%(table_name)s_%(constraint_name)s',
    }
)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


app.app_context().push()
with app.app_context():
    db.create_all()
# Models


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    author = db.Column(db.String(120))
    slug = db.Column(db.String(120))
    content = db.Column(db.String(1000))
    date_posted = db.Column(db.Date, default=datetime.utcnow)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    color = db.Column(db.String(100))
    date_added = db.Column(db.Date, default=datetime.utcnow)
    password_hash = db.Column(db.String(120))

    @property
    def password(self):
        raise AttributeError('password is not readable!!!!!!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def password_verify(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Users: {self.email}>'


class post_form(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    content = StringField("Content", validators=[
                          DataRequired()], widget=TextArea())
    submit = SubmitField('Submit')


class user_form(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    color = StringField("Favorite color")
    password_hash = PasswordField('Password', validators=[DataRequired(
    ), equal_to('password_hash2', message="password must match")])
    password_hash2 = PasswordField(
        'Confirm password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class name_form(FlaskForm):
    name = StringField("Enter your name", validators=[DataRequired()])
    submit = SubmitField('Submit')


class pw_form(FlaskForm):
    email = StringField("Enter your email :", validators=[DataRequired()])
    password_hash = PasswordField(
        "Enter your password :", validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField("Enter username :", validators=[DataRequired()])
    password = PasswordField("Enter your password :",
                             validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/login/', methods=['get', 'post'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Logged in successfully.')
                return redirect(url_for('dashboard'))
            else:
                flash('whops wrong password try again')
        else:
            flash('whops user does not exit')
    return render_template('login.html', form=form)


@app.route('/dashboard/', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/add_posts/', methods=["GET", "POST"])
@login_required
def add_posts():
    form = post_form()
    if form.validate_on_submit():
        post = Posts(
            title=form.title.data,
            author=form.author.data,
            slug=form.slug.data,
            content=form.content.data
        )
        form.title.data = ''
        form.author.data = ''
        form.slug.data = ''
        form.content.data = ''
        db.session.add(post)
        db.session.commit()
        flash('Post added successufly !!!')
    our_posts = Posts.query.order_by(Posts.title)
    return render_template('add_posts.html', our_posts=our_posts, form=form)


@app.route('/posts/')
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)


@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_posts(id):
    post = Posts.query.get_or_404(id)
    form = post_form()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        db.session.add(post)
        db.session.commit()
        flash('post edited successufly !!')
        redirect(url_for('posts', id=post.id))
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template('edit_posts.html', form=form)


@app.route('/posts/delete/<int:id>')
def delete_posts(id):
    delete_post = Posts.query.get_or_404(id)
    try:
        db.session.delete(delete_post)
        db.session.commit()
        flash('User deleted successufly!!!')
        return redirect(url_for('posts'))

    except:
        flash('Whoops try again')
        return redirect(url_for('posts'))


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = user_form()
    update_name = Users.query.get_or_404(id)
    # if form.validate_on_submit():
    #     update_name.name = form.name.data
    #     update_name.email = form.email.data
    #     update_name.color = form.color.data
    #     update_name.username = form.username.data
    if request.method == 'POST':
        update_name.name = request.form['name']
        update_name.email = request.form['email']
        update_name.color = request.form['color']
        update_name.username = request.form['username']
        try:
            db.session.commit()
            flash("user updated !!!")
            return render_template('update.html', form=form, update_name=update_name)
        except:
            flash("Error try again !!!")
            return render_template('update.html', form=form, update_name=update_name)
    else:
        return render_template('update.html', form=form, update_name=update_name, id=id)


@app.route('/delete/<int:id>')
def delete(id):
    delete_name = Users.query.get_or_404(id)
    name = None
    form = user_form()
    try:
        db.session.delete(delete_name)
        db.session.commit()
        flash('User deleted successufly!!!')
        our_users = Users.query.order_by(Users.name)
        return render_template('add_user.html', form=form, name=name, our_users=our_users)

    except:
        return render_template('add_user.html', form=form, name=name, our_users=our_users)


@app.route('/user/add/', methods=['GET', 'POST'])
def add_user():
    name = None
    form = user_form()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data)
            user = Users(name=form.name.data, username=form.username.data,
                         email=form.email.data, color=form.color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.color.data = ''
        form.password_hash.data = ''
        flash('user added successufly')
    our_users = Users.query.order_by(Users.name)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)


@app.route("/")
def index():
    first_name = 'luffy'
    stuff = "this a bold text"
    food = ["steak", "chiken", "pepperoni"]
    return render_template('index.html', first_name=first_name, stuff=stuff, food=food)


@app.route("/user/<name>")
def user(name):
    return render_template('user.html', user_name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/name/', methods=['GET', 'POST'])
def name():
    name = None
    form = name_form()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash('Submitted successufly')
    return render_template('name.html', name=name, form=form)


@app.route('/test_pw/', methods=['GET', 'POST'])
def test_pw():
    email = None
    password_hash = None
    pw_check = None
    passed = None
    form = pw_form()
    if form.validate_on_submit():
        email = form.email.data
        password_hash = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''
        pw_check = Users.query.filter_by(email=email).first()
        passed = check_password_hash(pw_check.password_hash, password_hash)
        flash('Submitted successufly')
    return render_template('test_pw.html', email=email, password_hash=password_hash, pw_check=pw_check, passed=passed, form=form)


@app.route('/date/')
def current_date():
    return {"Date": datetime.today()}
