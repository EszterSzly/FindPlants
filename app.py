from flask import Flask, abort, render_template, request, url_for, flash, redirect
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,login_user, logout_user,current_user,login_required
from flask_migrate import Migrate

from forms import RegistrationForm, LoginForm
from models import db, User, Comment,Plant, Location
from flask_mailman import Mail
from itsdangerous import URLSafeTimedSerializer

from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = "ecb37f3c46e781ff019f3aa16ff886300d04c74c89c999db169e41937477e7b6"


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config["MAIL_BACKEND"] = "console"


mail= Mail(app)

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

db.init_app(app)
migrate = Migrate(app, db)

bcrypt = Bcrypt (app)
login_manager = LoginManager(app)

login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def send_reset_email(user):
    token = serializer.dumps(user.email, salt='password-reset-salt')

    reset_url = url_for('reset_token', token=token, _external=True)

    subject = "Reset your password"
    message = f"""
    To reset your password, visit the following link:
    {reset_url}

    If you did not request this, simply ignore this email.
    """

    mail.send_mail(
        subject=subject,
        message=message,
        from_email= "noreply@findplants.com",
        recipient_list=[user.email]
    )



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
    query = request.args.get('query')  

    if not query:
        return render_template('search.html', plants=[], query=query)
    
    results = Plant.query.filter(
        (Plant.name.ilike(f"%{query}%")) |
        (Plant.description.ilike(f"%{query}%"))
        ).all()

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
            return redirect(url_for('login'))

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

@app.route("/plant/<int:plant_id>", methods=['GET', 'POST'])
def plant_detail(plant_id):
    plant=Plant.query.get_or_404(plant_id)
    google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY")


    if request.method == "POST":
        if not current_user.is_authenticated:
            flash("Please log in to comment.","warning")
            return redirect(url_for("login"))
        
        text = request.form.get("text")

        if text:
            new_comment = Comment(
                text=text,
                plant_id=plant.id,
                user_id=current_user.id
            )
            
            db.session.add(new_comment)
            db.session.commit()

        return redirect(url_for("plant_detail", plant_id=plant.id))
    
    return render_template(
        "plant_detail.html",
        plant=plant,
        locations=[
            {"latitude": l.latitude, "longitude": l.longitude}
            for l in plant.locations
        ],
     google_maps_key=google_maps_key
    )


@app.route("/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment=Comment.query.get_or_404(comment_id)

    if comment.author !=current_user:
        abort(403)
        
    db.session.delete(comment)
    db.session.commit()

    return redirect(url_for("plant_detail", plant_id=comment.plant_id))

@app.route("/save/<int:plant_id>", methods=["POST"])
@login_required
def save_plant(plant_id):
    plant=Plant.query.get_or_404(plant_id)

    if plant not in current_user.saved:
        current_user.saved.append(plant)
        db.session.commit()

    return redirect(url_for("plant_detail", plant_id=plant_id))

@app.route("/unsave/<int:plant_id>", methods=["POST"])
@login_required
def unsave_plant(plant_id):
    plant=Plant.query.get_or_404(plant_id)

    if plant in current_user.saved:
        current_user.saved.remove(plant)
        db.session.commit()

    return redirect(url_for("plant_detail", plant_id=plant_id))

@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        flash("The link is invalid or expired.", "warning")
        return redirect(url_for("forgot_password"))

    user = User.query.filter_by(email=email).first()

    if request.method == "POST":
        new_password = request.form.get("password")
        hashed_pw = bcrypt.generate_password_hash(new_password).decode("utf-8")
        user.password = hashed_pw
        db.session.commit()
        flash("Your password has been updated!", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html")

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()

        if user:
            send_reset_email(user)

        flash("If an account with that email exists, a reset link has been sent.", "info")
        return redirect(url_for("login"))

    return render_template("forgot_password.html")



if __name__ == '__main__':
  app.run(debug=True)
