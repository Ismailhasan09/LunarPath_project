from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import json
from flask_mail import Mail
from werkzeug.utils import secure_filename
import os

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)

mail = Mail(app)

if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(20), nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(50), nullable=False)
    Id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    img_file = db.Column(db.String(50), nullable=True)

# Ensure the upload folder exists
if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')

app.config['UPLOAD_FOLDER'] = 'static/uploads'

@app.route("/")
def home():
    return render_template('index.html', params=params)

@app.route('/about')
def about():
    return render_template('about.html', params=params)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_num=phone, msg=message, email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name, sender=email, recipients=[params['gmail-user']], body=message + "\n" + phone)
    return render_template('contact.html', params=params)

@app.route("/post", methods=['GET'])
def post_route():
    post = Posts.query.first()  # Or modify to filter by slug or other parameters
    return render_template('post.html', params=params, post=post)

@app.route("/add-post", methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        name = request.form.get('name')
        post_id = request.form.get('id')
        title = request.form.get('title')
        slug = request.form.get('slug')
        content = request.form.get('content')

        # Handle image upload
        file = request.files.get('img_file')
        img_filename = None
        if file and file.filename != '':
            img_filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))

        post = Posts(Name=name, Id=post_id, title=title, slug=slug, content=content, img_file=img_filename)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('all_posts'))

    return render_template('add_post.html', params=params)

@app.route("/edit/<int:sno>", methods=["GET", "POST"])
def edit_post(sno):
    post = Posts.query.get_or_404(sno)

    if request.method == "POST":
        post.Name = request.form.get("name")
        post.Id = request.form.get("id")
        post.title = request.form.get("title")
        post.slug = request.form.get("slug")
        post.content = request.form.get("content")

        if "img_file" in request.files:
            file = request.files["img_file"]
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                post.img_file = filename

        db.session.commit()
        return redirect(url_for("all_posts"))

    return render_template("edit_post.html", post=post)

@app.route("/delete/<int:sno>")
def delete_post(sno):
    post = Posts.query.get_or_404(sno)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("all_posts"))

@app.route('/all-posts')
def all_posts():
    posts = Posts.query.all()
    return render_template('all_posts.html', posts=posts, params=params)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        return render_template('dashboard.html')

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if username == params['admin_user'] and userpass == params['admin_password']:
            session['user'] = username
            return render_template('dashboard.html', params=params)

    return render_template('login.html', params=params)

# Initialize the database
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(port=5110, debug=True)
