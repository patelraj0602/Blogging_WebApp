from datetime import datetime
from flaskblog import db,login_manager
from flask_login import UserMixin
                                                                                                    #This db is the instance(object) of my SQLAlchemy(database).                                                      
                                                                                                    #https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#one-to-one(relationships)


# when we login in(automatically created when we use login_user method for login.)
# To do this we need login manager.

# Decorate the function load_user so that the extension know that This is the user to get by Id.
# This is used for reloading the user using user_id stored in the session created 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  
   

#Flask-Login can manage user sessions. Start by adding the UserMixin to your User model. The UserMixin will add Flask-Login attributes to the model so that Flask-Login will be able to work with it.
# we are inheriting from db.Model and UserMixin.
#https://stackoverflow.com/questions/63231163/what-is-the-usermixin-in-flask
class User(db.Model, UserMixin):                                                                    #This class(db model) creates an table inside database
                                                                                                    #Inheriting from user mixin class.
    id = db.Column(db.Integer, primary_key=True)                                                    #By default the table name is lowercase of class(user) but we can change it if we want to.
    username = db.Column(db.String(20), unique=True, nullable=False)                                #These are the columns of the table.
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)                                    #Used to create one-many relationships.



    # If anyone tries to print out a particular row(object of this class) of a table in an database
    # then by default they will have can only access the columns which are witten below.
    # To represent a object we use an repr method => https://www.youtube.com/watch?v=IIzOQhf5AKo
    def __repr__(self):                                                                             #This is used for printing the content of table.
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(100), nullable=False)  
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)                   
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)                       # This user_id(int Post table) has the id of the user(from User table) inside foreign key
                                                                                                    # That's how it creates one-many relationships accross different tables in database.
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

# Using backref(author) for any Post(by syntex : posts.author) then it will fetch  
# the "whole row" of that user from the User table.

# Also we can access all the Posts created by a particular user.