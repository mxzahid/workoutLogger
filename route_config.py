from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

# app reference
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'abdullah'
app.config['MYSQL_DB'] = 'workoutlogs'

mysql = MySQL(app)
# This method executes before any API request


@app.before_request
def before_request():
    print('before API request')


@app.route('/', methods=['GET', 'POST'])
def home():
    print('hello')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
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
    WHERE daily_logs.routine_date_id = (
        SELECT MAX(daily_logs.routine_date_id) FROM daily_logs
    )
    ;
    ''')
    latestRoutine = cursor.fetchall()
    routineMD = {'date': latestRoutine[0]['date'],
                 'name': latestRoutine[0]['routine_name'],
                 'type': latestRoutine[0]['type']
                 }
    return render_template("home.html", routineMD=routineMD, latestRoutine=latestRoutine)


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


# @app.route('/api/logs', methods=['GET'])
# def get_specified_logs():
#     x = request.form['numOfLogsRequested']
#     print("sjdkfhgkjsdfhglkjh")
#     print(x)
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # cursor.execute('''
    # SELECT daily_logs.date,
    # routines.routine_name,
    # routines.type,
    # exercises.name,
    # routine_date_exercise.sets,
    # routine_date_exercise.reps,
    # routine_date_exercise.weight
    # FROM daily_logs
    # JOIN routine_date_exercise
    #     ON routine_date_exercise.routine_date_id=daily_logs.routine_date_id
    # JOIN routine_exercises
    #     ON routine_date_exercise.routine_exercise_id=routine_exercises.routine_exercise_id
    # JOIN routines
    #     ON routine_exercises.routine_id=routines.routine_id
    # JOIN exercises
    #     ON routine_exercises.exercise_id=exercises.exercise_id
    # LIMIT ?
    # ;
    # ''', x)
    # return render_template('index.html')

    #     # This is POST method which stores students details.

    # @app.route('/api/new_entry', methods=['POST'])
    # def store_student_data():
    #     return "Student list[POST]"
    # # This method executes after every API request.


@app.after_request
def after_request(response):
    return response


if __name__ == '__main__':
    app.run(debug=True)
