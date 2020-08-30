from User import User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, request, render_template, redirect, url_for
import datetime

app=Flask("Tennis Reservation")
app.secret_key='very secret'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#key=court number
#value=dictionary
#      key=datetime.date object
#      value=dictionary
#            key=hour (int from 0-23) 
#            value=name of person who reserved it (string)
reservations = {1: {},
                2: {},
                3: {},
                4: {},    
    }
#key=username
#value=user object
accounts = {'mihika': User('mihika', 'fluffyducks', 1, 0, {})}

todayDate = datetime.date.today()
#reservations[1][todayDate] = { 
#    8: 'mihika', 
#    9: 'sharad'}
#reservations[1][todayDate][10] = 'shrey'

#not linked to a url, is a helper function that returns the user corresponsing to a userid
@login_manager.user_loader
def load_user(user_id):
    for user in accounts.values():
        if user.get_id() == str(user_id):
            return user
    return None

@app.route('/', methods=['GET'])
def loginPage():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    todayDateAsString = todayDate.isoformat()
    username = request.form['user']
    password = request.form['pass']
    if username not in accounts:
        return render_template('error.html', invalidUsername=username)
    if accounts[username].password != password:
        return render_template('error.html', invalidPassword=password)
    user = accounts[username]
    login_user(user)
    return redirect('view/court/1')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('loginPage'))
    
@app.route('/view/court/<int:court_num>/<date>', methods=['GET'])    #every variable in URL has to be defined as a function argument
@login_required
def viewForParticularDay(court_num, date):
    try:
        inputDate = datetime.date.fromisoformat(date)
    except:
        return render_template('error.html', invalidDate=date, court=court_num)
    if (court_num not in reservations):
        return render_template('error.html', invalidCourt=str(court_num), todayDateAsString=date)
    pDay = inputDate-datetime.timedelta(days=1)
    nDay = inputDate+datetime.timedelta(days=1)  
    return render_template('view.html',
                           name=current_user.username,
                           daySched=reservations[court_num].get(inputDate,{}),
                           day=inputDate,
                           num=court_num,
                           prevDay=pDay,
                           nextDay=nDay)  #sends the dictionary for the day's reservations  

@app.route('/view/court/<int:court_num>', methods=['GET'])
@login_required
def viewForToday(court_num):
    todayDate = datetime.date.today()
    todayDateString = todayDate.isoformat()  
    if court_num not in reservations:
        return render_template('error.html', invalidCourt=str(court_num), todayDateAsString=todayDateString)
    return redirect(url_for('viewForParticularDay', court_num=court_num, date=todayDateString))

#this is where the reservation is made, not at view.html
#receives the post request
@app.route('/view/court/<int:court_num>/<date>/hour/<int:hour>', methods=['POST'])
@login_required
def reserveCourt(court_num, date, hour):     
    try: 
        inputDate = datetime.date.fromisoformat(date)
    except:
        return render_template('error.html', invalidDate=date, court=court_num)
    if (court_num not in reservations):
        return render_template('error.html', invalidCourt=str(court_num), todayDateAsString=date)
    if inputDate not in reservations[court_num]:
        reservations[court_num][inputDate]={}
    if (current_user.hasBooked2Hours(inputDate) and current_user.isAdmin == 0):
        return render_template('error.html', tooManyHours='yes', court=court_num, todayDateAsString=date)
    reservations[court_num][inputDate][hour] = current_user.username
    pastReserve = current_user.get_pastReservations()
    if inputDate not in pastReserve:
        pastReserve[inputDate] = {}
    if court_num not in pastReserve[inputDate]:
        pastReserve[inputDate][court_num] = set()
    pastReserve[inputDate][court_num].add(hour)
    current_user.set_pastReservations(pastReserve)
    return redirect(url_for('viewForParticularDay', court_num=court_num, date=date))

#if i changed the cancel part of this url to be view, how would the view.html know which method to go to?
@app.route('/cancel/court/<int:court_num>/<date>/hour/<int:hour>', methods=['POST'])
@login_required
def deleteReservation(court_num, date, hour):
    try: 
        inputDate = datetime.date.fromisoformat(date)
    except:
        return render_template('error.html', invalidDate=date, court=court_num)
    if court_num not in reservations:
        return render_template('error.html', invalidCourt=str(court_num), todayDateAsString=date)
    if inputDate not in reservations[court_num]:
        return render_template('error.html', invalidDate=date, court=court_num)
    if hour not in reservations[court_num][inputDate]:
        return render_template('error.html', invalidHour=str(hour), todayDateAsString=date, court=court_num)
    if(reservations[court_num][inputDate][hour] != current_user.username and current_user.isAdmin == 0):
        return render_template('error.html', invalidDelete='yes', court=court_num, todayDateAsString=date)
    del reservations[court_num][inputDate][hour]
    pastReserve = current_user.get_pastReservations()
    pastReserve[inputDate][court_num].remove(hour)
    current_user.set_pastReservations(pastReserve)
    return redirect(url_for('viewForParticularDay', court_num=court_num, date=date))
