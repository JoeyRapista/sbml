from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_ckeditor import CKEditor

app = Flask(__name__)
ckeditor = CKEditor(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///joey.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://leswfjzczrpnnk:37b638d0c546f0a0f392a6917eaaf4c4b553121c6e32c74f1215e4f6a4c9af5a@ec2-3-222-204-187.compute-1.amazonaws.com:5432/d4ta0uv18bmlse'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "as#asdASASF#ASFLKsndvssdf2p2990$"

db = SQLAlchemy(app)
migrate = Migrate(app, db)



 
from sbml import routes