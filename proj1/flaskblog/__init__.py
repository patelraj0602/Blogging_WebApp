from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
 
app = Flask(__name__)                                               # Created an instance of the Flask Class.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False        
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)                               
login_manager.login_view = 'login'                                  # If we have used login_required decorate anywhere with in our apps. This this method(login_view) expects a function name where we would like to go if the user isn't loged in.
login_manager.login_message_category = 'info'                       # This is a bootstrap class for design purpose.(for alert message.)


from flaskblog import routes       