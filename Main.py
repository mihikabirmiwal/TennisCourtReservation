

from flask import Flask, request, render_template
import datetime

app = Flask("Tennis Reservation")

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

todayDate = datetime.date.today()
reservations[1][todayDate] = { 
    8: 'mihika', 
    9: 'sharad'}

reservations[1][todayDate][10] = 'shrey'

@app.route('/')
def login():
    return render_template('login.html')



    
@app.route('/view/court/<int:court_num>/<date>', methods=['GET'])    #every variable in URL has to be defined as a function argument
def viewForParticularDay(court_num, date):
    try:
        inputDate = datetime.date.fromisoformat(date)
    except:
        return render_template('error.html', invalidDate=date, court=court_num)
    if (court_num not in reservations):
        return render_template('error.html', invalidCourt=str(court_num), todayDateAsString=date)
    pDay = inputDate-datetime.timedelta(days=1)
    nDay = inputDate+datetime.timedelta(days=1)  
    return render_template('view.html', daySched=reservations[court_num].get(inputDate,{}), day=inputDate, num=court_num, prevDay=pDay, nextDay=nDay)  #sends the dictionary for the day's reservations  

@app.route('/view/court/<int:court_num>', methods=['GET'])
def viewForToday(court_num):
    todayDate = datetime.date.today()
    todayDateString = todayDate.isoformat()  
    if court_num not in reservations:
        return render_template('error.html', invalidCourt=str(court_num), todayDateAsString=todayDateString)
    return viewForParticularDay(court_num, todayDateString)

#this is where the reservation is made, not at view.html
#receives the post request
@app.route('/view/court/<int:court_num>/<date>/hour/<int:hour>', methods=['POST'])
def reserveCourt(court_num, date, hour):     
    try: 
        inputDate = datetime.date.fromisoformat(date)
    except:
        return render_template('error.html', invalidDate=date, court=court_num)
    if not request.form['user']:
        return render_template('error.html', invalidName='bad', court=court_num, todayDateAsString=date)  
    if (court_num not in reservations):
        return render_template('error.html', invalidCourt=str(court_num), todayDateAsString=date)
    if inputDate not in reservations[court_num]:
        reservations[court_num][inputDate]={}
    reservations[court_num][inputDate][hour] = request.form['user']
    return viewForParticularDay(court_num, date)

#if i changed the cancel part of this url to be view, how would the view.html know which method to go to?
@app.route('/cancel/court/<int:court_num>/<date>/hour/<int:hour>', methods=['POST'])
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
    del reservations[court_num][inputDate][hour]
    return viewForParticularDay(court_num, date)
