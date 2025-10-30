from flask import Flask, render_template, request, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
app = Flask(__name__)

app.config['SECRET_KEY']='24c20f22273ccbc827a9652c4db320bf'
posts = [
    {"title": "🌼 Did you know?", "content": "Dandelion isn’t just a weed — its leaves are packed with iron and can be eaten raw in salads!"},
    {"title": "🌿 Did you know?", "content": "The leaves of the stinging nettle lose their sting once cooked and are rich in plant protein and calcium."},
    {"title": "🌺 Did you know?", "content": "The cheerful calendula has natural healing properties.It’s often used in creams and teas to support skin health and reduce inflammation."}
]

@app.route('/')
@app.route('/home')
def index():

    return render_template("index.html", posts=posts)


@app.route('/search')
def search():
    query = request.args.get('query')  # for the searched word
    # later db or api
    return f"You are searching for '{query}' "

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect (url_for('index'))

    return render_template('register.html', title='Register', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        if form.email.data== 'eszter@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login unsuccesful. Please check username and password', 'danger')
    return render_template('login.html', title='Log in', form=form)

if __name__ == '__main__':
  app.run(debug=True)