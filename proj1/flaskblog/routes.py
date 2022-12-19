import secrets,os
from PIL import Image                                                                                                                            # To reduce the dimension of the image. 
from flask import render_template, url_for, flash, redirect,request, abort
from flaskblog import app,db,bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User,Post
from flask_login import login_user, current_user,logout_user, login_required

 
#decorator is simply a callable object that takes a function as an input parameter.
# More on decorators => https://www.youtube.com/watch?v=FsAPt_9Bf3U&t=1385s
@app.route("/") 
@app.route("/home")
def home():
    # I am paginating the posts.   
    page = request.args.get('page',1,type=int)                                                                                                  # page number should be compulasary an int.
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)                                                        # Order by helps to print the latest post at first(Remember all this features are given by SQLAlchemy including pagination.) # There is a special method if we want to paginate our website.
    # posts = Post.query.all()                                                                                                                  # To simply show everything on same page.
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():  
    return render_template('about.html', title='About')
 

@app.route("/register", methods=['GET', 'POST'])
def register():
    #print(request.method)                                                                                                                      #Playing with requests.(https://www.youtube.com/watch?v=ap2vxzAZVIg)
    #print(request.form)                                                                                                                        #In an way server is sending an empty form to the user end.
 
    if current_user.is_authenticated:                                                                                                           # To use this functionality we have inherit UserMixin in our User Model.(https://stackoverflow.com/questions/19532372/whats-the-point-of-the-is-authenticated-method-used-in-flask-login)
        return redirect(url_for('home'))
    form = RegistrationForm()                                                                                                                   #This is an instance of the Class RegistrationForm      
    if form.validate_on_submit():  
        hash_password = bcrypt.generate_password_hash(form.password.data)
        user = User(username = form.username.data, email = form.email.data, password = hash_password)
        db.session.add(user)
        db.session.commit()

        flash('Your account is successfully created go ahead and login','success')                                                              #success is an argument for styling purpose only.
        return redirect(url_for('login'))                                                                                                        #This home inside urlfor is the name of function not path.
    return render_template('register.html', title='Register', form=form)                                                                        #flash message=>the flash() method of the flask module passes the message to the next request which is an HTML template.


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:                                                                                                           #To fetch the details of the currently logged in user.
        return redirect(url_for('home'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):

            # (Step 9 of this article) MORE ABOUT login_user in this : https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login         
            # More on user sessions : https://www.youtube.com/watch?v=iIhAfX4iek0
            # UserMixin : https://stackoverflow.com/questions/63231163/what-is-the-usermixin-in-flask#:~:text=UserMixin%20class%20provides%20the%20implementation,method%20to%20do%20that%20yourself.

            login_user(user, remember=form.remember.data)                                                                                       # request: is simply an query.    args:Is an dictionnary key value pair.  . So we are accessing the value for key equal to next.
            next_page = request.args.get('next')                                                                                                # purpose: If you try to access account page without login then this help to redirect the uesr to the account page directly after login.
            if next_page:
                return redirect(url_for('account'))
            else:
                return redirect(url_for('home'))                                                                                                     

        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

# To save the updated picture in our database. Because sometimes the name of picture might collide with
# the picture name of other users.
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)                                                                                                       # Randomly creates 8 byte secret key
    _, f_ext = os.path.splitext(form_picture.filename)                                                                                      # split filename and extension.
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)                                                           # Storing the picture into static profile pics and getting its path into picture_path var
    form_picture.save(picture_path)                                                                                                         # Storing the picture at the above path.

    output_size = (125, 125)
    i = Image.open(form_picture)                                                                                                            # Reducing the dimensions of the pictures to save memory.
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required                                                                                                                             
def account():                                                                                                                              # This means to access /account route user should be loged in first.(For deatils refer __init__.py)
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file                                                                                          # We will store the picture name(which is present in static folder) into our database.

        current_user.username = form.username.data                                                                                          # Updating username and email i  our database.
        current_user.email = form.email.data
        db.session.commit()
        flash('You account details are upadated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename=f"profile_pics/{current_user.image_file}")                                                      # We will fetch the stored picture from the static directory. 
    return render_template('account.html', title='Account', image_file=image_file, form=form)
    

@app.route("/post/new", methods=['GET', 'POST'])
@login_required                                                                                                                             # User must be loged in first.
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data, content = form.content.data, author=current_user)                                              # For one-many reationships I have done using backred(author) but instead we can replace that with user_id = current_user.id
        db.session.add(post)
        db.session.commit()                                                                                                                # Simply inserting this post in our data base.
        flash('Your post has been created successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html',title='New Post',form=form, legend='Update Post')


@app.route("/post/<int:post_id>")                                                                                                          # To dynamically create an route.
def post(post_id):
    # We can directly get a row of that particular column by just using its ID using following syntex.
    post = Post.query.get_or_404(post_id)                                                                                                  # This method means get me the post for the given id and if it does not exist then give a 404 error.
    return render_template('post.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])                                                                                                
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id) 
    if post.author != current_user:
        abort(403)                                                                                                                         # Throwing error.
    
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been successfully updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

     
@app.route("/post/<int:post_id>/delete", methods=['GET', 'POST'])                                                                                                
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id) 
    if post.author != current_user:
        abort(403)                                                                                                                               # Throwing error.
    db.session.delete(post)                                                                                                                      # Syntex to delete a row from the table.
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page',1,type=int)    
    user = User.query.filter_by(username=username).first_or_404()                                                                                 # works same as get_or_404()   
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)     

    return render_template('user_post.html', posts=posts, user=user)
