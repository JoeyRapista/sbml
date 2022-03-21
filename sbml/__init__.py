from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_ckeditor import CKEditor

app = Flask(__name__)
ckeditor = CKEditor(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///joey.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://cgiowbcdqoyezw:16b9052877e5b125b0864764992b150e8aa75efcc58883f54de97897776187d9@ec2-3-231-254-204.compute-1.amazonaws.com:5432/d4e871oljt4tb5'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "as#asdASASF#ASFLKsndvssdf2p2990$"

db = SQLAlchemy(app)
migrate = Migrate(app, db)



 
from sbml import routes