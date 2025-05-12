from flask import Flask, render_template,request, session,redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import json
from flask_mail import Mail
from werkzeug.utils import secure_filename
import os


with open('config.json','r') as c:
   params= json.load(c) ["params"]
local_server=True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config.update(
    MAIL_SERVER= 'smtp.gmail.com',
    MAIL_PORT= 465,
    MAIL_USE_SSL= True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params ['gmail-password'])


mail=Mail(app)
if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI']= params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] =params['prod_uri']


# Correct URI with PyMySQL driver
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3308/lunar'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(20), nullable=False)

######the original
# class Posts(db.Model):
#     sno = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(80), nullable=False)
#     slug = db.Column(db.String(21), nullable=False)
#     content = db.Column(db.String(120), nullable=False)
#     img_file = db.Column(db.String(12), nullable=True)
##########################################################################

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(50), nullable=False)  # Added Name field
    Id = db.Column(db.Integer, nullable=False)  # Added Id field
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    img_file = db.Column(db.String(50), nullable=True)  # Updated to varchar(50)





##############
# with app.app_context():
#       db.create_all()
# ############### yoututube gomepage code
@app.route("/")
def home():
     return render_template('index.html',params=params)
##there was index.html in the login portion
#######################################



@app.route('/about')
def about():
    return render_template('about.html',params=params)

@app.route('/contact',methods = ['GET', 'POST'])
def contact():
    if request.method=='POST':
      name = request.form.get('name')
      email = request.form.get('email')
      phone = request.form.get('phone')
      message = request.form.get('message')
      entry = Contacts(name=name, phone_num = phone, msg = message, email = email )
      db.session.add(entry)
      db.session.commit()
      mail.send_message('New message from ' +name ,sender=email,recipients=[params['gmail-user']], body=message + "\n" + phone)


    return render_template('contact.html',params=params)

@app.route("/post", methods=['GET'])
def post_route():
    # Optionally load a specific post, or just return a static template
    post = Posts.query.first()  # or None
    return render_template('post.html', params=params, post=post)
###fast
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
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        else:
            filename = None  # If no file, store None

        # Create post object
        post = Posts(Name=name, Id=post_id, title=title, slug=slug, content=content, img_file=filename)
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

        # Handle image upload if a new file is provided
        if "img_file" in request.files:
            file = request.files["img_file"]
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                post.img_file = filename  # Save the new image filename to the database

        db.session.commit()  # Commit changes to the database
        return redirect(url_for("all_posts"))  # Redirect to the all posts page

    return render_template("edit_post.html", post=post, params=params)  # Pass params to the template


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

with app.app_context():
    db.create_all()

#################2nd fast#########################
@app.route('/submit-post', methods=['POST'])
def submit_post():
    if request.method == 'POST':
        name = request.form.get('name')
        post_id = request.form.get('id')
        title = request.form.get('title')
        content = request.form.get('content')

        # Creating a new post instance
        post = Posts(Name=name, Id=post_id, title=title, slug=title.replace(" ", "-").lower(), content=content)

        # Adding the new post to the session and committing it to the database
        db.session.add(post)
        db.session.commit()

        # Redirecting to the page where all posts are displayed
        return redirect(url_for('all_posts'))

    # If not a POST request, just return the submit form again (though this should not happen)
    return render_template('post.html', params=params)





app.config['UPLOAD_FOLDER'] = 'static/uploads'







###################think about later. this is slug function based problem
# @app.route("/post/<string:post_slug>", methods=['GET'])
# def post_route(post_slug):
#     post = Posts.query.filter_by(slug=post_slug).first()
#     return render_template('post.html', params=params, post=post)
####################-__----------##############



# @app.route('/post')
# def post():
#     return render_template('post.html',params=params)
# ##############################################################
@app.route('/dashboard',methods=['GET','POST'])
def dashboard():

     if 'user' in session and session['user']== params['admin_user']:
         # return render_template('dashboard.html')
         return render_template('dashboard.html')
     if request.method=='POST':
          username=request.form.get('uname')
          userpass=request.form.get('pass')
          if username==params['admin_user'] and userpass==params['admin_password'] :
              #set the session variable
               session ['user']= username
               return render_template('dashboard.html',params=params)
          #REDIRECT TO ADMIN PANEL

     return render_template('login.html',params=params)

#just looking for login
@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user' in session and session['user'] == params['admin_user']:
        return redirect("/dashboard")

    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email == params['admin_user'] and password == params['admin_password']:
            session['user'] = email
            return redirect("/dashboard")
        else:
            error = "Invalid Credentials. Please try again."

    return render_template('newchatgptlogin2.html', error=error, params=params)



# @app.route("/")
# def index():
#      return render_template("index.html", params=params)


app.run(port=5111, debug=True)


# kgigkgkg