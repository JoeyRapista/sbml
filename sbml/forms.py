import imghdr
from logging import PlaceHolder
from wtforms import StringField, SubmitField, PasswordField, SelectField, FieldList, IntegerField, BooleanField, FormField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea 
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField


class LoginForm(FlaskForm): 
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()]) 
	submit = SubmitField("Login")

class SeasonForm(FlaskForm): 
	name = StringField("Name", validators=[DataRequired()])
	description = StringField("Description", validators=[DataRequired()], widget=TextArea())  
	status = SelectField(u'Status', choices=['open', 'start', 'end'], validators=[DataRequired()])  
	reg_season_type = SelectField(u'Regular Season', choices=['Single Round Robin', 'Double Round Robin'], validators=[DataRequired()])  
	reg_season_max = IntegerField('Max Teams') 
	playoffs_type = SelectField(u'Playoffs', choices=['Single Elimination', 'Double Elimination'], validators=[DataRequired()])  
	playoffs_max = SelectField(u'Max Teams',choices=['4', '6'], validators=[DataRequired()])  
	submit = SubmitField("Submit")

class MatchForm(FlaskForm): 
	isDone = BooleanField("Match Done")  
	name = StringField("Name") 
	schedule = StringField("Match Schedule", validators=[DataRequired()])  
	yt_link = StringField("YouTube link") 
	team_a = SelectField(u'Team A', choices=['Team A', 'Team B', 'Team C'], validators=[DataRequired()])   
	team_a_score = IntegerField('Score') 
	team_b = SelectField(u'Team B', choices=['Team A', 'Team B', 'Team C'], validators=[DataRequired()])  
	team_b_score = IntegerField('Score')  
	team_winner = SelectField(u'Winner', choices=['Team A', 'Team B', 'Team C'], validators=[DataRequired()])   
	submit = SubmitField("Submit") 

class PlayerForm(FlaskForm):  
	full_name = StringField("Full name", validators=[DataRequired()])
	ml_id = StringField("ML ID", validators=[DataRequired()])
	ml_ign = StringField("ML IGN(ML name)", validators=[DataRequired()])
	role = SelectField(u'Role', choices=['MID', 'GOLD', 'EXP', 'JUNGLE', 'SUPPORT', 'COACH', 'SPONSOR', 'BENCH', 'WATER BOY', 'WATER GIRL'], validators=[DataRequired()])

class TeamForm(FlaskForm): 
	team_name = StringField("Team name", validators=[DataRequired()])
	logo_url = StringField("Team logo", validators=[DataRequired()]) 
	description = StringField("Tag line", validators=[DataRequired()], widget=TextArea()) 
	contact_number = StringField("Contact number", validators=[DataRequired()]) 
	player = FieldList(FormField(PlayerForm), min_entries=7, max_entries=8)
	submit = SubmitField("Submit")

class AwardsForm(FlaskForm): 
	team = SelectField(u'Team A', choices=['Team A', 'Team B', 'Team C'], validators=[DataRequired()])   
	place = StringField("Place", validators=[DataRequired()])  
	submit = SubmitField("Add award")

class LogosForm(FlaskForm):   
	url = StringField("url", validators=[DataRequired()]) 
	submit = SubmitField("Add logo") 

class RulesForm(FlaskForm): 
	rules = CKEditorField("Rules", validators=[DataRequired()]) 
	submit = SubmitField("Save")

class RoundRobinForm(FlaskForm): 
	start_date = StringField("Start date and Time", validators=[DataRequired()])  
	match_per_date = IntegerField('No. of match per date', validators=[DataRequired()]) 
	submit = SubmitField("submit")

class UsersForm(FlaskForm): 
	username = StringField("Username", validators=[DataRequired()])  
	password = PasswordField("Password", validators=[DataRequired()]) 
	submit = SubmitField("Add user")

class SponsorForm(FlaskForm): 
	name = StringField("Name", validators=[DataRequired()])  
	link = StringField("Link", validators=[DataRequired()])  
	logo = StringField("Logo", validators=[DataRequired()])   
	submit = SubmitField("Add sponsor")

class FourTeamsForm(FlaskForm): 
	rank1 = SelectField(u'Rank 1', choices=['Team A', 'Team B', 'Team C'], validators=[DataRequired()])    
	rank2 = SelectField(u'Rank 2', choices=['Team A', 'Team B', 'Team C'], validators=[DataRequired()])    
	rank3 = SelectField(u'Rank 3', choices=['Team A', 'Team B', 'Team C'], validators=[DataRequired()])    
	rank4 = SelectField(u'Rank 4', choices=['Team A', 'Team B', 'Team C'], validators=[DataRequired()])    
	submit = SubmitField("Proceed")

