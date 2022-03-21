from sbml import db, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column('username', db.String(255))
    password_hash = db.Column('password', db.String(255))  
    isAdmin = db.Column(db.Boolean, default=False) 
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    @property
    def password(self):
        raise AttributeError('Password incorrect') 
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    def __repr__(self):
        return f'<User: {self.username}>'

class Logos(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    logo_url = db.Column(db.String(255)) 
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<Logos: {self.logo_url}>'

class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(255)) 
    link = db.Column(db.String(255)) 
    logo = db.Column(db.String(255)) 
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<Logos: {self.logo_url}>'

class Rules(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    rules = db.Column(db.Text()) 
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<Rules: {self.rules}>'

class Season(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text())
    status = db.Column(db.String(100)) 
    achievers = db.relationship('AchievementsAssc', back_populates="season", cascade="all, delete") 
    teams = db.relationship('Team', backref='season', lazy=True, cascade="all, delete") 
    tournaments = db.relationship('Tournament', backref='season',cascade="all, delete", lazy=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<Season: {self.name}>'
 

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    logo_url = db.Column(db.String(255), nullable=True)
    description  = db.Column(db.Text()) 
    players = db.relationship('Player', backref='team',cascade="all, delete", lazy=True)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False) 
    achievements = db.relationship('AchievementsAssc', back_populates="team", cascade="all, delete")
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<Team: {self.name}>'

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255)) 
    ml_id = db.Column(db.String(255))
    ml_ign = db.Column(db.String(255)) 
    role = db.Column(db.String(255)) 
    team_id =  db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False) 
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<Player: {self.full_name}>'

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(255), nullable=True)
    schedule = db.Column(db.DateTime, default=datetime.utcnow)
    isDone = db.Column(db.Boolean, default=False)
    yt_id = db.Column(db.String(255), nullable=True) 
    team_a_score = db.Column(db.Integer, default=0)
    team_b_score = db.Column(db.Integer, default=0)

    team_a_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=True)
    team_b_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=True)
    team_winner_id = db.Column(db.Integer, db.ForeignKey("team.id"))

    team_a = db.relationship('Team', foreign_keys=[team_a_id])
    team_b = db.relationship('Team', foreign_keys=[team_b_id])
    team_winner = db.relationship('Team', foreign_keys=[team_winner_id])

    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)  
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<Match: {self.team_a_id}>'
 
class Tournament(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    type = db.Column(db.String(255)) 
    participants = db.Column(db.Integer)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)
    matches = db.relationship('Match', backref='tournament',cascade="all, delete", lazy=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<Tournament: {self.name}>'

class AchievementsAssc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'))
    place = db.Column('place', db.String(255))
    team = db.relationship('Team', back_populates = 'achievements', cascade="all, delete")
    season = db.relationship('Season', back_populates = 'achievers', cascade="all, delete")
    date_added = db.Column(db.DateTime, default=datetime.utcnow)