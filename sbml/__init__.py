from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_ckeditor import CKEditor

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///joey.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://frfkmnxwpuvuky:c256aa296020c2d5e27af56d89e6f22fe00a9d256e448832e31045b1739a2f75@ec2-54-160-109-68.compute-1.amazonaws.com:5432/d1jbbtsblqp0rc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "as#asdASASF#ASFLKsndvssdf2p2990$"

db = SQLAlchemy(app)
migrate = Migrate(app, db)



 
from sbml import routes