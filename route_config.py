from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from numpy import number
from datetime import datetime

# app reference
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'abdullah'
app.config['MYSQL_DB'] = 'workoutlogs'

mysql = MySQL(app)


routineNameIdMap = {
    'chest + triceps-heavy': 1,
    'chest + triceps-volume': 2,
    'back + biceps-heavy': 3,
    'back + biceps-volume': 4,
    'shoulder + legs-heavy': 5,
    'shoulder + legs-volume': 6
}


def getLatestLogID():
    q = '''
                SELECT routine_date_id
                FROM daily_logs
                ORDER BY routine_date_id DESC
                LIMIT 1
            '''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(q)

    id = cursor.fetchone()['routine_date_id']

    return int(id)


def getLastAddedLog():
    recentlyAddedLogID = getLatestLogID()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = '''
            SELECT daily_logs.date,
            routines.routine_name,
            routines.type,
            exercises.name,
            routine_date_exercise.sets,
            routine_date_exercise.reps,
            routine_date_exercise.weight
            FROM daily_logs
            JOIN routine_date_exercise
                ON routine_date_exercise.routine_date_id=daily_logs.routine_date_id
            JOIN routine_exercises
                ON routine_date_exercise.routine_exercise_id=routine_exercises.routine_exercise_id
            JOIN routines
                ON routine_exercises.routine_id=routines.routine_id
            JOIN exercises
                ON routine_exercises.exercise_id=exercises.exercise_id
            where daily_logs.routine_date_id = %s
            ;
            '''
    val = (int(recentlyAddedLogID),)
    cursor.execute(query, val)
    recentlyAddedLog = cursor.fetchall()
    return recentlyAddedLog


def getR_d_e_idFromRoutineDateID(routineDateID):
    query = '''
    SELECT r_d_e_id
    FROM routine_date_exercise
    WHERE routine_date_id=%s ORDER by r_d_e_id LIMIT 1;
    '''
    val = (routineDateID,)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(query, val)
    obj = cursor.fetchone()
    r_d_e_id = obj['r_d_e_id']
    return r_d_e_id


def getMostRecentLogByDate():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = '''
    SELECT daily_logs.date,
    routines.routine_name,
    routines.type,
    exercises.name,
    routine_date_exercise.sets,
    routine_date_exercise.reps,
    routine_date_exercise.weight
    FROM daily_logs
    JOIN routine_date_exercise
        ON routine_date_exercise.routine_date_id=daily_logs.routine_date_id
    JOIN routine_exercises
        ON routine_date_exercise.routine_exercise_id=routine_exercises.routine_exercise_id
    JOIN routines
        ON routine_exercises.routine_id=routines.routine_id
    JOIN exercises
        ON routine_exercises.exercise_id=exercises.exercise_id
    WHERE daily_logs.date = (
        SELECT MAX(daily_logs.date) FROM daily_logs
    )
    ;
    '''
    cursor.execute(query)
    latestLog = cursor.fetchall()
    return latestLog


@app.before_request
def before_request():
    print('before API request')


@app.route('/', methods=['GET', 'POST'])
def home():
    latestLog = getMostRecentLogByDate()
    global latestLogDate
    latestLogDate = latestLog[0]['date']
    logMD = {'date': latestLog[0]['date'],
             'name': latestLog[0]['routine_name'],
             'type': latestLog[0]['type']
             }
    return render_template("home.html", routineMD=logMD, latestRoutine=latestLog)


@app.route('/workout_routines', methods=['GET', 'POST'])
def get_workout_routines_list():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
    SELECT routines.routine_name, routines.type,
    exercises.name, routine_exercises.default_sets,
    routine_exercises.default_reps
    FROM routine_exercises
    JOIN exercises ON routine_exercises.exercise_id=exercises.exercise_id
    JOIN routines
	ON routines.routine_id=routine_exercises.routine_id;''')
    allRoutines = cursor.fetchall()
    routineNames = {}
    for routine in allRoutines:
        nameType = (routine['routine_name'], routine['type'])
        if nameType not in routineNames.keys():
            routineNames[nameType] = []
        routineNames[nameType].append(
            (routine['name'], routine['default_sets'], routine['default_reps']))

    return render_template("routines.html", routines=routineNames)


@app.route('/logs', methods=['GET'])
def get_specified_logs():
    return render_template('getLogs.html', maxDate=latestLogDate)


@app.route('/logsByDate', methods=['POST'])
def get_log_by_date():
    if request.method == 'POST':
        oneLogDate = request.form.get('oneLogDate', None)
        if(oneLogDate != None):
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            query = '''
            SELECT daily_logs.date,
            routines.routine_name,
            routines.type,
            exercises.name,
            routine_date_exercise.sets,
            routine_date_exercise.reps,
            routine_date_exercise.weight
            FROM daily_logs
            JOIN routine_date_exercise
                ON routine_date_exercise.routine_date_id=daily_logs.routine_date_id
            JOIN routine_exercises
                ON routine_date_exercise.routine_exercise_id=routine_exercises.routine_exercise_id
            JOIN routines
                ON routine_exercises.routine_id=routines.routine_id
            JOIN exercises
                ON routine_exercises.exercise_id=exercises.exercise_id
            WHERE daily_logs.date = '{}'
            ;
            '''.format(oneLogDate)
            cursor.execute(query)
            oneDateLog = cursor.fetchall()
            oneDateLogMD = {'date': oneDateLog[0]['date'],
                            'name': oneDateLog[0]['routine_name'],
                            'type': oneDateLog[0]['type']
                            }

            return render_template('getLogs.html', maxDate=latestLogDate, oneDateLogMD=oneDateLogMD, oneDateLog=oneDateLog)
    return render_template('getLogs.html', maxDate=latestLogDate)


@app.route('/logsByNumber', methods=['POST'])
def get_n_recent_logs():
    if request.method == 'POST':
        numberOfLogsReq = request.form.get('numberOfLogs', None)
        if(numberOfLogsReq != None):
            queryForLastNroutineDateIds = '''
                SELECT routine_date_id
                FROM daily_logs
                ORDER BY routine_date_id DESC
            '''.format(numberOfLogsReq)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(queryForLastNroutineDateIds)
            lastNroutineDateIdObj = cursor.fetchall()
            routineDateIds = []
            for routineDateObj in lastNroutineDateIdObj:
                routineDateId = routineDateObj['routine_date_id']
                routineDateIds.append(routineDateId)

            nLogs = []
            nLogsMD = []
            for routineDateId in routineDateIds:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                query = '''
                SELECT daily_logs.date,
                routines.routine_name,
                routines.type,
                exercises.name,
                routine_date_exercise.sets,
                routine_date_exercise.reps,
                routine_date_exercise.weight
                FROM daily_logs
                JOIN routine_date_exercise
                    ON routine_date_exercise.routine_date_id=daily_logs.routine_date_id
                JOIN routine_exercises
                    ON routine_date_exercise.routine_exercise_id=routine_exercises.routine_exercise_id
                JOIN routines
                    ON routine_exercises.routine_id=routines.routine_id
                JOIN exercises
                    ON routine_exercises.exercise_id=exercises.exercise_id
                where daily_logs.routine_date_id = {}
                ;
                '''.format(routineDateId)
                cursor.execute(query)
                currLog = cursor.fetchall()
                currLogMD = {'date': currLog[0]['date'],
                             'name': currLog[0]['routine_name'],
                             'type': currLog[0]['type']
                             }
                nLogsMD.append(currLogMD)
                nLogs.append(currLog)

            return render_template('getLogs.html', maxDate=latestLogDate, nLogs=nLogs, nLogsMD=nLogsMD, n=len(nLogs))

    return render_template('getLogs.html', maxDate=latestLogDate)


@app.route('/addLog', methods=['GET', 'POST'])
def addLog():

    if request.method == 'POST':
        routineName = request.form.get('workout')
        routineType = request.form.get('type')
        logDate = request.form.get('logDate')
        if routineName == '':
            return render_template("addLog.html", missingMessage="Please add a routine name")
        if routineType == '':
            return render_template("addLog.html", missingMessage="Please add a routine type")
        routine = routineName + '-' + routineType
        routineId = routineNameIdMap[routine.lower()]
        query = "INSERT INTO daily_logs(date,routine_id) VALUES (%s, %s)"
        vals = (logDate, routineId)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query, vals)
        # x = cursor.fetchall()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        args = [int(routineId), logDate]
        cursor.callproc('addRoutineExercisesToLogs', args)
        mysql.connection.commit()

        # recentlyAddedLogID = getLatestLogID()
        recentlyAddedLog = getLastAddedLog()

        return render_template("addLog.html", recentlyAddedLog=recentlyAddedLog)
    return render_template("addLog.html")


@app.route('/addSetsReps', methods=['POST'])
def addSetsReps():
    if request.method == 'POST':
        f = request.form
        setRepWeightObj = {}
        counter = 0
        for key in f.keys():
            counter = 0
            for value in f.getlist(key):
                setRepWeightObj[key+str(counter)] = value
                counter += 1

        latestLogId = getLatestLogID()

        r_d_e_id = getR_d_e_idFromRoutineDateID(latestLogId)

        query = '''
        UPDATE routine_date_exercise
        SET sets = %s, reps= %s, weight=%s
        WHERE routine_date_id = %s AND r_d_e_id = %s;
        '''
        x = []
        for i in range(counter):
            currSetVal = setRepWeightObj['sets'+str(i)]
            currRepVal = setRepWeightObj['reps'+str(i)]
            currWeightVal = setRepWeightObj['weight'+str(i)]
            x.append((currSetVal, currRepVal, currWeightVal))

        for i in range(counter):
            vals = (x[i][0], x[i][1], x[i][2],
                    latestLogId, r_d_e_id+i)

            print(vals)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(query, vals)
            mysql.connection.commit()
        success = True
        return render_template("addLog.html", success)


@ app.after_request
def after_request(response):
    return response


if __name__ == '__main__':
    app.run(debug=True)
