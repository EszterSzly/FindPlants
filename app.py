from flask_bcrypt import Bcrypt
from flask_login import login_user, UserMixin, logout_user,current_user,login_required
from flask_login import LoginManager
from datetime import datetime
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm


app = Flask(__name__)
app.config['SECRET_KEY']='24c20f22273ccbc827a9652c4db320bf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt (app)
login_manager = LoginManager(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(20), unique=True, nullable=False)
    email= db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60),nullable=False)

    def __repr__(self):
         return f"User('{self.username}','{self.email}','{self.password}')"
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Comments(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     text = db.Column(db.Text, nullable=False)
     date_commented = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
     plant_id = db.Column(db.Integer, db.ForeignKey('plant.id'), nullable=False)

     def __repr__(self):
        return f"Comments('{self.text[:30]}','{self.date_commented}')"


class Plant(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latin_name= db.Column(db.String(120))
    description = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=True, default='default.jpg')
    comments = db.relationship('Comments', backref='plant', lazy=True)

    def __repr__(self):
        return f"Plant('{self.name}','{self.latin_name}','{self.image_file}')"

   



posts = [
    {"title": "🌼 Did you know?", "content": "Dandelion isn’t just a weed — its leaves are packed with iron and can be eaten raw in salads!"},
    {"title": "🌿 Did you know?", "content": "The leaves of the stinging nettle lose their sting once cooked and are rich in plant protein and calcium."},
    {"title": "🌺 Did you know?", "content": "The cheerful calendula has natural healing properties.It’s often used in creams and teas to support skin health and reduce inflammation."},
    {"title": "🌸 Did you know?", "content": "Elderflowers aren’t just beautiful — they’re packed with antioxidants and have natural anti-inflammatory properties. Traditionally, elderflower tea is used to ease cold symptoms and support the immune system."}
]

@app.route('/')
@app.route('/home')
def index():

    return render_template("index.html", posts=posts)


@app.route('/search')
def search():
    query = request.args.get('query')  # for the searched word
    # later db or api
    if not query:
        return render_template('search.html', plants=[])
    
    results = Plant.query.filter(Plant.name.ilike(f"%{query}%")).all()

    return render_template('search.html', plants=results, query=query)

@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect (url_for('login'))
    return render_template('register.html', title='Register', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user= User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You have been logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login unsuccesful. Please check username and password', 'danger')
    return render_template('login.html', title='Log in', form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out!', 'info')
    return redirect(url_for('index'))

@app.route("/account")
@login_required
def account():
    return render_template("account.html", title="My Account")


if __name__ == '__main__':
  app.run(debug=True)