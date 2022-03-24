from queue import Empty
from datetime import datetime, timedelta 
from sqlalchemy import or_
from flask import render_template, flash, request, redirect, url_for, abort
from flask_login import login_user, LoginManager, login_required, logout_user, current_user 
 
from urllib.parse import urlparse, parse_qs
from contextlib import suppress

from sbml.models import *
from sbml.forms import *
from sbml import app


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    previous_season = Season.query.filter(Season.status == 'end').all()
    season = Season.query.filter(Season.status != "end").first() 
    form = LoginForm()
    if form.validate_on_submit(): 
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Logged in successfully") 
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Wrong Credentials')
        else:
            flash('Wrong credentials')
    return render_template('login.html',season = season, previous_season=previous_season, form = form) 

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	flash("You logged out")
	return redirect(url_for('login'))



@app.route('/admin/rules', methods=['GET', 'POST'])
@login_required
def admin_rules():
    season = Season.query.filter(Season.status != "end").first()
    previous_season = Season.query.filter(Season.status == 'end').all()
    rules = Rules.query.first()
    form = RulesForm()
    if form.validate_on_submit(): 
        rules.rules = form.rules.data   
        db.session.add(rules)
        
        db.session.commit()
        flash('Rules updated')
    form.rules.data = rules.rules
    return render_template('admin_rules.html',form=form,rules=rules,season = season, previous_season=previous_season)

@app.route('/admin/logos',methods=['GET', 'POST'])
@login_required
def admin_logos():
    season = Season.query.filter(Season.status != "end").first()
    previous_season = Season.query.filter(Season.status == 'end').all()
    logos = Logos.query.all()
    form = LogosForm()
    if form.validate_on_submit():
        logo = Logos(logo_url=form.url.data)
        db.session.add(logo)
        db.session.commit()
        flash('Logo added')
        return redirect(url_for('admin_logos'))

    return render_template('admin_logos.html',logos=logos, form = form, season = season, previous_season=previous_season)

@app.route('/admin/logos/delete/<int:lid>')
@login_required
def admin_logos_delete(lid):
    logo = Logos.query.get_or_404(lid)
    try:
        db.session.delete(logo)
        db.session.commit()
        flash("Logo deleted")
        return redirect(url_for('admin_logos'))
    except:
        flash("Something wrong happned deleting the record, please try again")
        return redirect(url_for('admin_logos'))



@app.route('/admin/season/awards/<int:sid>', methods=['GET', 'POST'])
@login_required
def season_awards(sid):
    previous_season = Season.query.filter(Season.status == 'end').all()
    season = Season.query.filter(Season.status != "end").first()   
    s_season = Season.query.get_or_404(sid)
    return render_template("season_awards.html", s_season = s_season, season = season, previous_season = previous_season)

@app.route('/admin/season/awards/add/<int:sid>', methods=['GET', 'POST'])
@login_required
def season_awards_add(sid):
    previous_season = Season.query.filter(Season.status == 'end').all()
    season = Season.query.filter(Season.status != "end").first()   
    s_season = Season.query.get_or_404(sid)
    form = AwardsForm()
    team_options = [(t.id, t.name) for t in Team.query.filter_by(season_id=sid)]     
    form.team.choices = team_options
    if form.validate_on_submit():  
        award = AchievementsAssc(place=form.place.data)
        award.season = s_season 
        award.team_id = form.team.data
        db.session.add(award)
        db.session.commit()
        flash('Award added')
        return redirect(url_for('season_awards', sid=s_season.id))
    return render_template("season_awards_add.html", form=form, s_season = s_season, season = season, previous_season = previous_season)

@app.route('/admin/season/awards/<int:aid>/<int:sid>')
@login_required
def season_awards_delete(aid, sid):
    s_awards = AchievementsAssc.query.get_or_404(aid)
    try:
        db.session.delete(s_awards)
        db.session.commit()
        flash("Award deleted")
        return redirect(url_for('season_awards', sid=sid))
    except:
        flash("Something wrong happned deleting the record, please try again")
        return redirect(url_for('season_awards', sid=sid))



@app.route('/admin/dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard(): 
    
    previous_season = Season.query.filter(Season.status == 'end').all()
    season = Season.query.filter(Season.status != "end").first() 
    seasons = Season.query.all() 
    return render_template("admin.html", seasons = seasons, season = season, previous_season = previous_season)

 

@app.route('/admin/season/matches/<int:sid>', methods=['GET', 'POST'])
@login_required
def season_matches(sid): 
    
    previous_season = Season.query.filter(Season.status == 'end').all()
    season = Season.query.filter(Season.status != "end").first()  

    c_season = Season.query.filter_by(id=sid).first()
    return render_template("season_mod.html",  c_season = c_season, season = season, previous_season = previous_season)


@app.route('/admin/season/add', methods=['GET', 'POST'])
@login_required
def season_add(): 
    previous_season = Season.query.filter(Season.status == 'end').all()
    season = Season.query.filter(Season.status != "end").first() 
    form = SeasonForm()
    if season:
        flash('Please end previous season/s before adding new season.')
        return redirect(url_for('admin_dashboard'))
      
    if form.validate_on_submit():
        reg_season = Tournament(name="Regular Season", type=form.reg_season_type.data, participants = form.reg_season_max.data)
        playoffs = Tournament(name="Playoffs",type=form.playoffs_type.data, participants=int(form.playoffs_max.data) )
        season = Season(name=form.name.data, description=form.description.data, status=form.status.data) 
        season.tournaments.append(reg_season)
        season.tournaments.append(playoffs)
        db.session.add_all([season, reg_season, playoffs])
        db.session.commit()
        form.name.data = ''
        form.description.data = '' 
        flash('Season added') 
        return redirect(url_for('admin_dashboard'))
    return render_template("season_add.html", form = form,
    season = season, previous_season = previous_season) 


@app.route('/admin/season/edit/<int:sid>', methods=['GET', 'POST'])
@login_required
def season_edit(sid):
    previous_season = Season.query.filter(Season.status == 'end').all()
    season = Season.query.filter(Season.status != "end").first() 
    s_season = Season.query.get_or_404(sid)
    form = SeasonForm() 
    if form.validate_on_submit(): 
        s_season.name = form.name.data
        s_season.description = form.description.data
        s_season.status = form.status.data
        for t in s_season.tournaments:
            if t.name == 'Regular Season':
                t.type = form.reg_season_type.data
                t.participants = form.reg_season_max.data
                db.session.add(t)
            if t.name == 'Playoffs':
                t.type = form.playoffs_type.data
                t.participants = int(form.playoffs_max.data)
                db.session.add(t)
        db.session.add(s_season)
        db.session.commit() 
        flash('Season Updated') 
        return redirect(url_for('admin_dashboard'))
    form.name.data = s_season.name
    form.description.data = s_season.description
    form.status.data = s_season.status
    for t in s_season.tournaments:
        if t.name == 'Regular Season':
            form.reg_season_type.data = t.type
            form.reg_season_max.data = t.participants
        if t.name == 'Playoffs':
            form.playoffs_type.data = t.type
            form.playoffs_max.data = str(t.participants)
    return render_template("season_edit.html", form = form, s_season= s_season, season = season, previous_season = previous_season)


@app.route('/admin/delete/season/<int:sid>')
@login_required
def season_delete(sid):
    s_season = Season.query.get_or_404(sid)
    try:
        db.session.delete(s_season)
        db.session.commit()
        flash("Season Deleted Successfully")
        return redirect(url_for('admin_dashboard'))
    except:
        flash("Something wrong happned deleting the record, please try again")
        return redirect(url_for('admin_dashboard'))

 
@app.route('/admin/add/matches/auto-play-offs/<int:sid>/<int:tid>', methods=['GET', 'POST'])
@login_required
def auto_play_offs(sid, tid): 
    s_tournament = Tournament.query.get_or_404(tid)
    s_season = Season.query.get_or_404(sid) 
    if s_tournament.participants == 4 and s_tournament.type == 'Single Elimination': 
        m1 = Match(name='Match 1', tournament_id=s_tournament.id)
        m2 = Match(name='Match 2',tournament_id=s_tournament.id)
        m3 = Match(name='Match 3',tournament_id=s_tournament.id)
        db.session.add_all([m1,m2,m3])
        db.session.commit()
        return redirect(url_for('season_matches', sid=s_season.id))
        
    if s_tournament.participants == 6 and s_tournament.type == 'Single Elimination': 
        m1 = Match(name='Match 1', tournament_id=s_tournament.id)
        m2 = Match(name='Match 2',tournament_id=s_tournament.id)
        m3 = Match(name='Match 3',tournament_id=s_tournament.id)
        m4 = Match(name='Match 4',tournament_id=s_tournament.id)
        m5 = Match(name='Match 5',tournament_id=s_tournament.id)
        db.session.add_all([m1,m2,m3,m4,m5])
        db.session.commit()
        return redirect(url_for('season_matches', sid=s_season.id))

    if s_tournament.participants == 8 and s_tournament.type == 'Single Elimination': 
        m1 = Match(name='Match 1', tournament_id=s_tournament.id)
        m2 = Match(name='Match 2',tournament_id=s_tournament.id)
        m3 = Match(name='Match 3',tournament_id=s_tournament.id)
        m4 = Match(name='Match 4',tournament_id=s_tournament.id)
        m5 = Match(name='Match 5',tournament_id=s_tournament.id)
        m6 = Match(name='Match 6',tournament_id=s_tournament.id)
        m7 = Match(name='Match 7',tournament_id=s_tournament.id)
        db.session.add_all([m1,m2,m3,m4,m5,m6,m7])
        db.session.commit()
        return redirect(url_for('season_matches', sid=s_season.id))

    if s_tournament.participants == 4 and s_tournament.type == 'Double Elimination': 
        m1 = Match(name='Match 1',tournament_id=s_tournament.id)
        m2 = Match(name='Match 2',tournament_id=s_tournament.id)
        m3 = Match(name='Match 3',tournament_id=s_tournament.id)
        m4 = Match(name='Match 4',tournament_id=s_tournament.id)
        m5 = Match(name='Match 5',tournament_id=s_tournament.id)
        m6 = Match(name='Match 6',tournament_id=s_tournament.id) 
        db.session.add_all([m1,m2,m3,m4,m5,m6])
        db.session.commit()
        return redirect(url_for('season_matches', sid=s_season.id))

    if s_tournament.participants == 6 and s_tournament.type == 'Double Elimination': 
        m1 = Match(name='Match 1',tournament_id=s_tournament.id)
        m2 = Match(name='Match 2',tournament_id=s_tournament.id)
        m3 = Match(name='Match 3',tournament_id=s_tournament.id)
        m4 = Match(name='Match 4',tournament_id=s_tournament.id)
        m5 = Match(name='Match 5',tournament_id=s_tournament.id)
        m6 = Match(name='Match 6',tournament_id=s_tournament.id) 
        m7 = Match(name='Match 7',tournament_id=s_tournament.id) 
        m8 = Match(name='Match 8',tournament_id=s_tournament.id) 
        m9 = Match(name='Match 9',tournament_id=s_tournament.id) 
        m10 = Match(name='Match 10',tournament_id=s_tournament.id) 
        db.session.add_all([m1,m2,m3,m4,m5,m6,m7,m8,m9,m10])
        db.session.commit()
        return redirect(url_for('season_matches', sid=s_season.id)) 

    
@app.route('/admin/add/matches/auto-play-offs-restart/<int:sid>/<int:tid>', methods=['GET', 'POST'])
@login_required
def auto_play_offs_restart(sid, tid): 
    s_tournament = Tournament.query.get_or_404(tid)
    s_season = Season.query.get_or_404(sid)  
    for m in s_tournament.matches:
        try:
            db.session.delete(m)
            db.session.commit() 
        except:
            flash("Something wrong happned deleting the record, please try again")
            return redirect(url_for('season_matches', sid=s_season.id)) 
    return redirect(url_for('season_matches', sid=s_season.id))

@app.route('/admin/sponsors',methods=['GET', 'POST'])
@login_required
def admin_sponsors():
    previous_season = Season.query.filter(Season.status == 'end').all()
    season = Season.query.filter(Season.status != "end").first() 
    sponsors = Sponsor.query.all()
    form = SponsorForm()

    if form.validate_on_submit():
        sponsor = Sponsor(name=form.name.data, link=form.link.data, logo=form.logo.data)
        db.session.add(sponsor)
        db.session.commit() 
        flash('Sponsor added')
        return redirect(url_for('admin_sponsors'))
    return render_template('admin_sponsors.html',sponsors=sponsors,form=form, season = season, previous_season = previous_season)

@app.route('/admin/pfpmvvmweisdifnie/delete/sponsor/<int:spid>')
@login_required
def admin_sponsor_delete(spid):
    sponsor = Sponsor.query.get_or_404(spid)
    try:
        db.session.delete(sponsor)
        db.session.commit()
        flash("Sponsor Deleted Successfully")
        return redirect(url_for('admin_sponsors')) 
    except:
        flash("Something wrong deleting record, try again.")
        return redirect(url_for('admin_sponsors')) 


@app.route('/admin/users',methods=['GET', 'POST'])
@login_required
def admin_users():
    previous_season = Season.query.filter(Season.status == 'end').all()
    season = Season.query.filter(Season.status != "end").first() 
    users = User.query.all()
    form = UsersForm()

    if form.validate_on_submit():
        pass_hash = generate_password_hash(form.password.data, 'sha256')
        user = User(username=form.username.data, password_hash=pass_hash)
        db.session.add(user)
        db.session.commit()
        flash('User added')
        return redirect(url_for('admin_users'))
    return render_template('admin_users.html',users=users,form=form, season = season, previous_season = previous_season)

@app.route('/admin/pfpmvvmweisdifnie/delete/user/<int:uid>')
@login_required
def admin_user_delete(uid):
    users = User.query.all()
    ucount = len(users)
    if ucount <= 1:
        abort(403)
    user = User.query.get_or_404(uid)
    try:
        db.session.delete(user)
        db.session.commit()
        flash("User Deleted Successfully")
        return redirect(url_for('admin_users')) 
    except:
        flash("Something wrong deleting record, try again.")
        return redirect(url_for('admin_users'))

@app.route('/admin/add/matches/auto-round-robin/<int:sid>/<int:tid>', methods=['GET', 'POST'])
@login_required
def auto_round_robin(sid, tid):
    
    previous_season = Season.query.filter(Season.status == 'end').all()
    season = Season.query.filter(Season.status != "end").first() 
    s_tournament = Tournament.query.get_or_404(tid)
    s_season = Season.query.get_or_404(sid) 
    form = RoundRobinForm()
    if s_tournament.name != 'Regular Season':
        abort(403)  
    if not s_season.teams:
        flash('No teams registered')
        return redirect(url_for('season_matches', sid=s_season.id))

    teams = [] 
    for t in s_season.teams:
        teams.append(t.id)
    if form.validate_on_submit(): 
        arranged_teams = generateRoundRobin(teams)   
        start_date = datetime.strptime(form.start_date.data, '%Y-%m-%dT%H:%M')
        match_per_date = form.match_per_date.data
        ttl_mtch = int(len(arranged_teams))
        total_days_of_matches = int(ttl_mtch/match_per_date) 
        for i in range(total_days_of_matches): 
            oneday = timedelta(days=i)
            sched = start_date + oneday
            for j in range(match_per_date):
                next_hour = timedelta(hours=j)
                sched = sched+next_hour
                match = arranged_teams.pop(0) 
                new_match = Match(schedule = sched, team_a_id = match[0],team_b_id=match[1], tournament_id = s_tournament.id )
                db.session.add(new_match)
                db.session.commit()
        return redirect(url_for('season_matches', sid=s_season.id))

    return render_template('auto_round_robin.html',form=form,s_season=s_season, s_tournament = s_tournament, season = season, previous_season = previous_season)

def generateRoundRobin(teams):
    #append dummy element in the list if the team's length is odd
    if not len(teams) % 2 == 0:
         teams.append("Bye")   

    #get the number of teams
    teamCounts = len(teams) 
    #get the number of round, this will be used on how many times to loop
    rounds = teamCounts-1
    #get the middle will be used for apending each team by pairs
    teamHalfLen = teamCounts//2
    #init pairs list, append later generated list pair
    pairs = []
    #splitting the list
    firstHalf = teams[:teamHalfLen]
    secondHalf = teams[teamHalfLen:]
    #reverse the secondhalf, I just followed how the roundrobin algo works
    secondHalf.reverse() 
    
    #start looping in number of rounds e.g.
    for i in range(rounds):
        #loops to the length of the half which is expected to be equal with the other half
        for j in range(teamHalfLen): 
            #conditional if either of the pair is bye then dont append to the pairs list otherwise append to the list
            if not(firstHalf[j] == "Bye" or secondHalf[j] == "Bye"):
                pair = [firstHalf[j], secondHalf[j]]
                pairs.append(pair)   
            #either the both of the bye or not the lists should be rotated for the next round
            firstHalf, secondHalf = rotateList(firstHalf, secondHalf)
    return pairs

def rotateList(firstList, secondList): 
    #get the length of the list to be used to remove the last elemt in the list
    flen = int(len(firstList))
    #remove the last elemt in the list and store to itemFromfirst
    itemFromfirst = firstList.pop(flen-1)
    #remove the first element in the second list and store in itemFromSecond
    itemFromsecond = secondList.pop(0)
    
    #add the item at the second position in the first list
    firstList.insert(1, itemFromsecond)
    #add the item at the last position in the second list 
    secondList.append(itemFromfirst)

    #return
    return firstList, secondList

@app.route('/admin/add/match/<int:sid>/<int:tid>', methods=['GET', 'POST'])
@login_required
def match_add(sid, tid): 
    previous_season = Season.query.filter(Season.status == 'end').all()
    season = Season.query.filter(Season.status != "end").first() 
    s_season = Season.query.get_or_404(sid)
    s_tournament = Tournament.query.get_or_404(tid)
    form = MatchForm() 
    if s_season.teams: 
        team_options = [(t.id, t.name) for t in Team.query.filter_by(season_id=sid)] 
        blank_option =  ('0', 'None')
        team_options.insert(0, blank_option) 
        form.team_a.choices = team_options
        form.team_b.choices = team_options 
        form.team_winner.choices = team_options

        if form.validate_on_submit():
            sched_f = datetime.strptime(form.schedule.data, '%Y-%m-%dT%H:%M') 
            team_a = form.team_a.data  
            team_b = form.team_b.data  
            team_winner = form.team_winner.data  
            if team_a == 0:
                team_a = None
            if team_b == 0:
                team_b = None
            if team_winner == 0:
                team_winner = None
            match = Match(name=form.name.data, 
                    schedule = sched_f,
                    isDone=form.isDone.data,
                    yt_id=form.yt_link.data, 
                    team_a_score = form.team_a_score.data,
                    team_b_score = form.team_b_score.data, 
                    team_a_id=team_a,
                    team_b_id=team_b,
                    team_winner_id=team_winner,
                    tournament_id = tid
                    )
            db.session.add(match)
            db.session.commit() 
            flash('Match added.')   
            return redirect(url_for('season_matches', sid=sid))  

    else:
        flash('No teams registered')
        return redirect(url_for('season_matches', sid=sid)) 
    return render_template('match_add.html',form=form,s_season=s_season, s_tournament = s_tournament, season = season, previous_season = previous_season)

@app.route('/admin/edit/match/<int:sid>/<int:tid>/<int:mid>', methods=['GET', 'POST'])
@login_required
def match_edit(sid,tid,mid): 
    previous_season = Season.query.filter(Season.status == 'end').all()
    season = Season.query.filter(Season.status != "end").first() 
    match = Match.query.get_or_404(mid)
    s_season = Season.query.get_or_404(sid)
    s_tournament = Tournament.query.get_or_404(tid)
    special_case_match_name = match.name
    team_a_select = match.team_a_id
    team_b_select = match.team_b_id
    team_winner_select = match.team_winner_id

    if team_a_select == None:
        team_a_select = 0
    if team_b_select == None:
        team_b_select = 0
    if team_winner_select == None:
        team_winner_select = 0 

    form = MatchForm(team_a=team_a_select, team_b=team_b_select, team_winner = team_winner_select) 
    team_options = [(t.id, t.name) for t in Team.query.filter_by(season_id=sid)] 
    blank_option =  (0, 'None')
    team_options.insert(0, blank_option) 
    form.team_a.choices = team_options
    form.team_b.choices = team_options  
    form.team_winner.choices = team_options

    if form.validate_on_submit():
        team_a = form.team_a.data  
        team_b = form.team_b.data  
        team_winner = form.team_winner.data  
        if team_a == 0:
            team_a = None
        if team_b == 0:
            team_b = None
        if team_winner == 0:
            team_winner = None
        sched_f = datetime.strptime(form.schedule.data, '%Y-%m-%dT%H:%M')  
        if match.tournament.name == 'Playoffs':
            match.name = special_case_match_name
        else:
            match.name = form.name.data
        match.isDone = form.isDone.data
        match.schedule = sched_f
        match.yt_id = form.yt_link.data
        match.team_a_score = form.team_a_score.data
        match.team_b_score = form.team_b_score.data
        match.team_a_id = team_a
        match.team_b_id = team_b
        match.team_winner_id = team_winner
        db.session.add(match)
        db.session.commit() 
        
        flash('Match updated.')   
        return redirect(url_for('season_matches', sid=sid))  
    form.name.data = match.name
    form.isDone.data = match.isDone
    form.schedule.data = match.schedule.strftime('%Y-%m-%dT%H:%M')
    form.yt_link.data = match.yt_id 
    form.team_a_score.data = match.team_a_score
    form.team_b_score.data = match.team_b_score  
    return render_template('match_edit.html',form=form, s_season=s_season, s_tournament = s_tournament, season = season, previous_season = previous_season)

@app.route('/admin/delete/match/<int:sid>/<int:mid>')
@login_required
def match_delete(sid,mid):
    match = Match.query.get_or_404(mid)
    try:
        db.session.delete(match)
        db.session.commit()
        flash("Match Deleted Successfully")
        return redirect(url_for('season_matches', sid=sid)) 
    except:
        flash("Something wrong happned deleting the record, please try again")
        return redirect(url_for('season_matches', sid=sid)) 

@app.route('/register', methods=['GET', 'POST'])
def register():
    season = Season.query.filter(Season.status != "end").first()
    sponsors = Sponsor.query.all()
    if season.status != 'open':
        abort(403)
    max = None
    regteams = len(season.teams) 
    for t in season.tournaments:
        if t.name == "Regular Season":
            max = t.participants
    if regteams >= max:
        flash('Ooopss! Maximum teams reached for the season.')
        return redirect(url_for('index')) 
    form = TeamForm()
    logos = Logos.query.all()
    previous_season = Season.query.filter(Season.status == 'end').all()
    if form.validate_on_submit(): 
        team = Team(name=form.team_name.data, logo_url=form.logo_url.data, description=form.description.data, contact_number=form.contact_number.data,  season_id=season.id ) 
        for p in form.player:  
                player = Player(full_name=p.full_name.data, ml_id=p.ml_id.data, ml_ign=p.ml_ign.data, role=p.role.data)
                db.session.add(player)
                team.players.append(player)
        db.session.add(team)
        db.session.commit()
        logo_to_delete = Logos.query.filter_by(logo_url=form.logo_url.data).first()
        try:
            db.session.delete(logo_to_delete)
            db.session.commit()
        except:
            flash('Something wrong with the logo but dont worry your team is still registered.')
        flash('Team registered!')
        return redirect(url_for('index')) 
    return render_template('register.html',sponsors=sponsors,logos = logos, form=form, season = season, previous_season=previous_season)


@app.route('/')
def index():
    season = Season.query.filter(Season.status != "end").first()
    previous_season = Season.query.filter(Season.status == 'end').all()
    sponsors = Sponsor.query.all()
    team_converted = []
    if not season is None: 
        teams = season.teams 
        for t in teams: 
            ms = Match.query.filter(or_(Match.team_a_id==t.id, Match.team_b_id==t.id)).all()
            win_count = 0
            loss_count = 0
            match_count = 0
            for w in ms:
                if w.tournament.name == 'Regular Season':
                    match_count = match_count+1
                if w.tournament.name == 'Regular Season' and w.isDone:
                    if  w.team_winner_id == t.id:
                        win_count = win_count+1 
                    else:
                        loss_count = loss_count+1
                
            temp_teams = [t.id, t.name, win_count, loss_count, t.logo_url, match_count]
            team_converted.append(temp_teams) 
        sort_rank(team_converted)
 
    playoffs_matches = [] 
    if not season is None: 
        for tmt in season.tournaments:
            if tmt.name == 'Playoffs':
                for m in tmt.matches: 
                    schedule_month = str(m.schedule.strftime('%b')) 
                    schedule_day = str(m.schedule.day)
                    schedule_hour = str(m.schedule.strftime('%I'))
                    schedule_min = str(m.schedule.strftime('%M')) 
                    schedule_p = str(m.schedule.strftime('%p'))
                    m_sched = f'{schedule_month}-{schedule_day} {schedule_hour}:{schedule_min} {schedule_p}' 
                    temp_ms = [m.id, m.name, m.team_a, m.team_b, m.team_a_score, m.team_b_score, m.team_winner, m.isDone, m_sched]  
                    playoffs_matches.append(temp_ms)
    return render_template('index.html', sponsors=sponsors,playoffs_matches = playoffs_matches, team_converted = team_converted, season = season, previous_season=previous_season)

# take second element for sort
def takeWins(elem):
    return elem[2]

def sort_rank(teams):   
    sorted = teams.sort(key=takeWins, reverse=True)  
    return sorted



@app.route('/teams')
def teams():
    season = Season.query.filter(Season.status != "end").first()
    sponsors = Sponsor.query.all()
    if season is None:
        abort(403)
    previous_season = Season.query.filter(Season.status == 'end').all()
    return render_template('teams.html', sponsors=sponsors,previous_season=previous_season, season = season)

@app.route('/team/<int:t_id>')
def team_view(t_id):
    season = Season.query.filter(Season.status != "end").first()
    team = Team.query.get_or_404(t_id)
    previous_season = Season.query.filter(Season.status == 'end').all()
    sponsors = Sponsor.query.all()

    matches = Match.query.filter(or_(Match.team_a_id==team.id, Match.team_b_id==team.id)).all()
    
    return render_template('team_view.html',sponsors=sponsors,season = season, previous_season=previous_season, team = team, matches = matches)

@app.route('/rules')
def rules():
    season = Season.query.filter(Season.status != "end").first()
    previous_season = Season.query.filter(Season.status == 'end').all()
    rule = Rules.query.first()
    sponsors = Sponsor.query.all()

    return render_template('rules.html',sponsors=sponsors,rule=rule,season = season, previous_season=previous_season)

@app.route('/match/view/<int:mid>')
def match_view(mid):
    season = Season.query.filter(Season.status != "end").first()
    previous_season = Season.query.filter(Season.status == 'end').all()
    sponsors = Sponsor.query.all()

    match = Match.query.get_or_404(mid) 
    match_yt_id = get_yt_id(match.yt_id)
    return render_template('match_view.html',sponsors=sponsors,match=match,match_yt_id=match_yt_id, season = season, previous_season=previous_season)

def get_yt_id(url, ignore_playlist=False):
    # Examples:
    # - http://youtu.be/SA2iWivDJiE
    # - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    # - http://www.youtube.com/embed/SA2iWivDJiE
    # - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    query = urlparse(url)
    if query.hostname == 'youtu.be': return query.path[1:]
    if query.hostname in {'www.youtube.com', 'youtube.com', 'music.youtube.com'}:
        if not ignore_playlist:
        # use case: get playlist id not current video in playlist
            with suppress(KeyError):
                return parse_qs(query.query)['list'][0]
        if query.path == '/watch': return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/watch/': return query.path.split('/')[1]
        if query.path[:7] == '/embed/': return query.path.split('/')[2]
        if query.path[:3] == '/v/': return query.path.split('/')[2]

@app.route('/schedules')
def schedules():
    season = Season.query.filter(Season.status != "end").first()
    sponsors = Sponsor.query.all()
     
    if season is None:
        abort(403)
    previous_season = Season.query.filter(Season.status == 'end').all()

    return render_template('schedules.html',sponsors=sponsors,season = season, previous_season=previous_season)

@app.route('/season/<int:s_id>')
def season_view(s_id): 
    previous_season = Season.query.filter(Season.status == 'end').all()
    s_season = Season.query.filter_by(id=s_id).first() 
    sponsors = Sponsor.query.all()

    season = Season.query.filter(Season.status != "end").first()
    return render_template('season_view.html',sponsors=sponsors, season = season, s_season = s_season, previous_season=previous_season)