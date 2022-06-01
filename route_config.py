from django.shortcuts import render
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import hashlib

# app reference
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'abdullah'
app.config['MYSQL_DB'] = 'workoutlogs'
app.secret_key = 'your secret key'

mysql = MySQL(app)


routineNameIdMap = {
    'chest + triceps-heavy': 1,
    'chest + triceps-volume': 2,
    'back + biceps-heavy': 3,
    'back + biceps-volume': 4,
    'shoulder + legs-heavy': 5,
    'shoulder + legs-volume': 6
}

routineNamePicMap = {
    'Chest + Triceps-H': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAoHCBESEhIRERIREhERERERERERERERERERGBQZGRgUGBgcIS4lHB4rIRgYJjgmKy8xNTU1HCQ7QDs0Py40NTEBDAwMDw8QGhISGjUhISExNDE0PT80NDQxMTE0NDQ0NDQ0NDE0MTQ/NDQ0NDE0MTQ0NDE0NDQ0NDQxMTQ0MTQ0NP/AABEIALcBEwMBIgACEQEDEQH/xAAcAAABBQEBAQAAAAAAAAAAAAADAAECBAUGBwj/xABKEAACAQIDBAYEBw0HBQEAAAABAgADEQQSIQUxQVEGEyJhcZFSgcHRBxQykqGxsiMkQlNic3SCk6LC0uEWVGNkcoPwMzRE0/EV/8QAGAEBAQEBAQAAAAAAAAAAAAAAAAECAwT/xAAdEQEBAQADAQEBAQAAAAAAAAAAARECAyExElFB/9oADAMBAAIRAxEAPwDyERxEBJASNFEI8cCZCtFaStHtCox7R7RAQERFaPaK0BrRASVorQI2jyVossCMUnaILGCEeTyxWjBCNaEtGtLghaKTtFaMEIpO0bLGCEVpK0aQNaNaSiMCJEiZMxoRG0iRJxjAHGkzImaDWiiigwQCPaSCx7QIgSQEQEcQEBHtHAkgIEcsQWEAjhZMVALFlhMsWWMEAIssnlkssoHaPaECR8kIEFjhYULHywA5Y+SHCxZYFfLFlh8sWWAArGyw5SRywBZY1oUrGKwBWjFYUrGywA2jEQxWMVgAIiIhCsiRJghGMkRGIlEbSJEJaRYQB2ikrRQCgSVo9ogIDASQEcCSAgNaSCyNR1UXY+A4mBGOX0W+iDVoLJZY2HqK4uvDeDvENlgDyx7QgEcLAGFkwsmFkwkAISPlhwkWWALJFaFyxZYA8sfLCWiywBZIikLlitACVkcssFZErAAViyQ2WIrAAUkSsOUkSsABWRKw9pHLACVkGSHeygk2AG+UWx44Lp46wJMJExJiVY2tYndxBkiIEYzCStGtAjaKKKAaPaICOICAk1ESiNXNkY/knzOkIzMRUzMTw3DwgwY0UqNDCUjkashF6RXrEv2jTY2zgcQDYHkSs01ExsHiDTa+8MrIw4FWUqfrv4gTX2ac1Ne66+R0+i0KKqyYWVtiq1WsUZ2tlcixGhBAGh8ZeCakd8hqKpJhJNEkwsLoOWLLDZYssGhZYssMEj5INV8sfLD5IskGgZY2WHyRZINAyxissFI2SDVfLGtLBSLJAr2kWWWisEywarFZErLGLoWw1SqGYMrootoBdlue/wCVKWzmZkJYkkORc3P4IPtg0LE0i4fWyUkFSob8SQqqO8kzGJ8JfxOLJR0Gi1KvWMbasFBVBfkLtpM+Vkpo0nzKDx3HxmdLuB1DDkQfP/5JVgpEYwjLIGFQtFHigGEkLd0ojBn0l48/dGODbhY+uE1orbmPODxtsjai/Z+sSj8Tqej9IjPhXUFiNBxuDKARRRQgtGmWNlFzYn1TZ6P6q45OD5j+kzMHh2ckAlQBcvYgAAjeZPB0KjrUamWumW6pmBa5OunhA1uigviiOS1PtLNPq9T4mYWwtmvWq5VrdUxRnzqczAAgFTYgg6y2NiVP7y+/0W/mgaNZ0poXckKLDcSSTuEojblC9stQa78q2HfvvAYzYrpTd2rs4QZspVrHW3pd8wAfGFjvEQEBhqCAQRuIO4yYpd0wtlbKeqpzVa1PLlsutsrC446acORHOXv7On+8Vv8Anrg+NDqe6P1J5SsNgU+NTFH/AHFH8El/+DS/GYr9rT/khB+pPIx+oPIyq/R+kRbPiR39ah+pBB/2ap/jMR89P5YF3qTyMbqe6VafR2kpvnxB7usp+1D9UKdhU/TxP7Sn/wCuAU0TyjdSeUC2wqfp4n9pT/klep0dQkkVq4vuuyn6gIF1qJ5StjaqUUzve17AAak8pXbo5yxFXyv7ZjbYwDUWCl2ZSAykjedQdL90LPV4bdpHejj5p9s0cl9RexFxod04u4nSHYLj/wAhvDIf5oRp4yn941zbc6nyZDMbZJ+5VG5Ox8kEsVdhOMPVq/GXKpvQobPu3nP38jumLh8M7BipORVZmIOgspNiOZt9MAIotkz27N8v9fCAlsYcmnnDEi+UqAdDrv8ArlQwFLeAYAtcgdniQOMqQtGiz3tbTfc2gaDOvpL85ZAuvpL84SqcI/d5xxhTxIHnIvo+dfSXzEUF8UHpj5pig2rYklkBJrCirFiEvTcfkk+WvsiWFWVHOiECSWIpZWZeR08DuhES/t8eMIbLxOs2+jCdl25uo8gffMatovedBOn2DQyUlvpmu59ensgVehAvi2/NOf31m4qTE6AC+Lf8y5/fSdEiQAY2kWo1lAFzSfebblv7JwWGF2Ua3JAFjbeZ6PiUHU1cxZV6t8xUgNbKb2M4bo/QFTE0VIuC4J9WvskrXH677D4XIoS5Nt7HeTz+oeAEKKctCnCilKzbqkKUkKUvLRkhRhGf1UXUzSFCOaMDL6mN1U0zQkeplGaaUi1KaZpQb0pBmmlMrpFhwcO5K5imUjmLsASPOdE1OUdrU/uFb80/2TFa43LK80wtFnqKqfKZgF1A18TO8qjWcj0eNsVT7yw9ZRvbado6QULErfBYvuQn6B7pzewFzUqw5m3mpnU1k+8sZ+bY/umcx0YYZai3F8ykLcXIsbm0IwkXeJF0tLeLpZKzLwzG3s+i3nBOkCsRNLZi9l25kDyH9ZnPvmzQTKirxtmPidYEWg2MI0E0jSEUUUAgk1gxJLAMsMsAsKplAcfhM4DL8pRa3pL75QoG/ZJs3CbaGHRQTqAfEAwyycHs9qjjMbgHUgWAHvnR4nBLVTqySq9m2Xhl3DvEjSFt0u0BrKMv4P3DYs2VVy4Zh2b3btpqbnfOiRN05z4NFvi3/R2+2k6umug8BAz9v1OrwdY8WUIP12Cn6CZx3ReoFxdAncagXzBA+udR02YjCqB+FWUHvAVzbzt5Ti9lsRWpkbw6nyma1xexJSh1pQ9NL2PMAywlKaYVVoSa0JeSjDLQgZwoR+o7ppijEaMoyzQkDQmqaMiaMDJahANRmy1GV6lGQY705lbfIp4aux/Fsvrbsj650j05ynTklcMVH4bjyGvukvxeP157suplr023WqIT4ZhPQqqTzKmbMD3z1OqLgHmAfokjVV6i/eeN7qLn9x5x/R+ktR3qFQrUwoULovaDC5Hqnasv3nj/AMw/2HnGdFN1b/b/AI5WRdtYPP2wDcaG2/Tc3smMwCi7Nc8NLGdVU3yrVgc/g8MXbMw7N+Wh7h3TSqGFeAcw1AmgmhGgWMgjFGvFAmDJqYIGTBgGQwymBQwimAdJZSVUMtIZUW6UvUN4HE7hxPhM8OEVnO5FLG2+wF5ymOxZq1GqWy3sFF75QAABCOp+DBfvup+jt9tJ1tFdBOF6E4t1xNOnTv1tSrSVCNzLms9Nh6JBLacVE7yhuAlGF08T70p8xXXyyP8A0nD7LqKlamz/ACQ1z4T1jaGyqeLpGk+h1NN/QexAbvGtiOU8ixOHem703BV0ZkZTwYGxEzWpXuuwq61sPRqKbhkS/EhwLMp7wQZrpSnhnRrpFWwNUMhLU2I6yiT2HHsbk3snuuxsbRxVJK9Bs6OP1lbijDgw5SypZg6UoZaMspThlpysqgoxdULgaXN7C4ubC5sOMbbuPXCYepXYBiq2RPxlQ/ITwv8AQDPn3bHSPFVMUtZ8TVerSclHRii0id4pKDZRw7+N43Fk19BNRgzRnN/B70nfGq9DEMHrIoqU6gRUNSnuYELYFgdbgC4O7TXtGpyy6lmMqpSlapSmvUpypUpwMarT7p5v0621TZ+oRlfIjhypBAdiNARyA18Ze6e9L1ObCYR7jVa1ZDoeaIeI5n1DjPNmMxfW+Mz1Kit2A3d/Ad89YxCW05aeU5DodsTrCcRUW9NDamCNHfj4qPrNuBnY4iIloSLfDY4f4B+xUnDdEz/1vCn/ABTvcIL0caP8A/YqTz3ZD5HAo3qrUCCr2GU0u88OJ8ZUbdSU6kt1JUqGFV3ld4dzKzmFgTmCYybGDeQRvFI3ihUgZMGBBkwYB1aFUysphlaEWkMs0zKSNLFNpStCi0x8TsKqzuUCZCWZO1bQnRAOBHlNOm8vUXhEfgxo0XxAujGtTFSrn4BfuaIB39uoT+rynSYU6DwE5z4KBfGVP0Y/bT3TewbaL4CEbeGnN9O+jBrIcXQW9RFvWQb6iAfLA4so38wO7XocM02MKd0pK+eRN/op0mr4CqHpnMjECrRY9iovfybk3DwuD0fTroQ9Mvi8IhaixLVqSAs1FjvdVG9OOnyfDd53eZsblfRmxunmzMRlHXig5AumIBp2PLP8g+c6TFbSwtFOtrV6NOna4d6ihW/069r1T5SWoY9SqWJJPcO4DQAd0stTlJ/j1b4Rum+DxVNaWFqs1g1yaVRBcspv2wOCi08rAS+/Tib2PlK5N40eJtdf0K2/SwWJSpUd+rVlBKoWYJnUsLd65h657TgOnmyK+i4tFa4Fq6vQvfdYsAp9RnzRHBiJbr6V2x0y2bhQc+KR2H4FD7s5PLsaL+sRPKumPwhVMWpo4ZWoUG+X2gatQeixGir+SL34kjScIahYLck5Rb1cJAyW2tSQ5M2OjOw3xlYUxdaa2aq/opfh+UdwHidwMh0f2BiMbU6uimgtnqMCKdNebNz5AamewbL2RSwVEUaWv4TuRZqj21Y8uQHAfSwvJVOHSmi00UKiKFRRwA9vfM7EGaeJbfMjEPKyNs7WnjB/l2+w8896Nb6v+hPrM9C2LquLHOg32X98866PmzP30x9DCBs1GlSo0NUaVKjQqDtKzmTdoBzIqDGCcyTGCYwps8UaKAhJgwYMQaAdWhFaVwYRWgWkaWKbSijQ6NCNGm8uU3+qZlN5YSp9UpjS+Cn/ALur+jfxpNbB1NF8BMf4KzbF1T/l/wCNJbwlTsr4D6oiV0uFqTawr7py+GrTawuI3So6jCvunLdLvg5oYwNWwoShitWKABaNc7+0B8hj6Q05jiNvC1902cNW3SVY+ZcdgalCo9KsjJUpsVem4swYcD9BvuIIMz5638OOzlzYXFqAC4fD1DzKdpD5M49QnkkkLSiiilQooooBKZ1tz0ncdBeg7Y8mtWLU8JTaxYfLrOLXROQF9W4bhc3twgn0xsXBjCYTD4YWvSooHsLXqEZnb1uWMmerviNLC0sPTWjQppTp0x2UQWHeTxJPEnUzNxT75exNffMTF15UxRxL75k4l5axNWZWJqQrW6PG/wAYHOi3tHtnnGxGs7fmz9pffPQejD3qVRzoN9tR7Z51so2f/bP2lgazvKtR5N3lV2kVF2gWMdzAs0BMYJjHYyJMKUUjeKE0riOGEFHjDaMGHOSDjnAWitHh6tq45iFSovMecohZIKe7yl8M5fxqJXX0h5w6119JfMTGAPd5Qig93lG8T88/46n4N6ypiKzubKMPqbEn5a8BLNKm6AAjUAA8dZx2GNQkpTzlnsMqBi7EG9gBqd0eulZCQ4qowtcPnUi+64MJjvaeIA3/AFGaGH2lTG9rfqv7p5er1Dopc+BcyYWtyreTxsX817BhtuURvqW/Uqe6atDpHhhb7qPmP7p4YExHKv5VJCpVqqbO9VTvszOptzsY2U/NjvvhV6TU8QtDCUmzrTY16rAEAPYqia8QCxOn4Q755pCO5Ykklid5JJJ9ZkLQmGjyRA0kbQWGikyBI2gsEoPldWKhgrKSrfJYA3ynuNp9AYnpFhm7S1kZW7SsDoQdQZ8+XlmnjaoAUVKigaAB2AA5WvBj2attqib2qJ5zLxO0aZ3OvnPMPjVb8ZV+e/vjfG6v4yp+0f3wuO/q4pTuI85RqMTunH/Hav4yp89vfHGNrfjKnz2geg9GCVrPn7Iai6Lfi2dDbyDTgMAbNr6BH0iTo7VrqykValwQbFyb2N7SmX1vCNWo0ruZnmr/AMuZEt/y8GrjtAMYC8aTDRWMheRijDUrxSMUppRRRQhR7xRQHzGSFQxRSH6qQqHulujuBO+KKZ5fHo6rbfVrYlc0sbQccKyKf9NTst9DGdp0g2XTrYlmcsV6umrKpKk1RfW/ILYRRTX+Ry5+cqzH2LSRkbD5lyhutzsWJJ+Rbute/qlqnhGHFfp90UU5dvXxt9duns5cZ4JjcSMNSaqe0VtlAvqx0APdz7hPPsVXeq5eoSzObkmKKXq6+PHch3dvPnZLQL23RrxRTo4HWPFFCz4a8aKKEpSRAjxQR1PRraDVB8Xa5KqTTYn8Eb1Phw7tOU1quDY8B5xRThy6uN5WvXw7eX4kUcRs6oQQAL2Nu0N9oD+zCWRuvIcqjOvV3COQCQDfUDURRTp18ZJ44dvO8r613pfF9kVAwBZusVhvAd6oUW8BY3nnzRRTo5IRoooQooooCiiigKKKKB//2Q==',
    'Chest + Triceps-V': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS71SeZ0AKo4nNT7HSKMLsendQanOeAH9eriQ&usqp=CAU',
    'Back + Biceps-H': 'data:image/jpeg;base64,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',
    'Back + Biceps-V': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT8S4NrKeL8Fiddv3K5kmQBMQtxp9Bq_47_hA&usqp=CAU',
    'Shoulder + Legs-H': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTTB38nTx22utuscV_r-9fydr4GoCfvAFlwJw&usqp=CAU',
    'Shoulder + Legs-V': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTed4z8tlwVc_dNz2msRjnW_68gRI_a4OcDCg&usqp=CAU',
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


def doesLogExistByDate(date):
    checkLogExistsQuery = '''
                SELECT COUNT(*)
                FROM daily_logs
                WHERE daily_logs.date=%s
            '''
    val = (date,)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(checkLogExistsQuery, val)
    count = cursor.fetchall()
    count = count[0]['COUNT(*)']
    if(count == 0):
        return False
    else:
        return True


def getPasswordHash(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def doesUsernameExist(username):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = '''
        SELECT * FROM users WHERE username = %s 
    '''
    vals = (username,)
    cursor.execute(query, vals)
    result = cursor.fetchall()
    if result:
        return True
    return False


def validatePassword(password):
    specialCharArray = ['!', '@', '#', '$']
    isValid = True
    message = ''
    if len(password) < 8:
        message = 'password must be more than 8 characters'
        isValid = False
    if len(password) > 20:
        message = 'password must be less than 20 characters'
        isValid = False
    if not any(char.isdigit() for char in password):
        message = 'password must contain at least one digit'
        isValid = False
    if not any(char.isupper() for char in password):
        message = 'password must contain at least one uppercase letter'
        isValid = False
    if not any(char.islower() for char in password):
        message = 'password must contain at least one lowercase letter'
        isValid = False
    if not any(char in specialCharArray for char in password):
        message = 'password must contain at least one special character letter'
        isValid = False
    return [isValid, message]


@app.before_request
def before_request():
    pass


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

    return render_template("routines.html", routines=routineNames, pics=routineNamePicMap)


@app.route('/logs', methods=['GET', 'POST'])
def get_specified_logs():
    return render_template('getLogs.html', maxDate=latestLogDate, displayGetLogOptions=True)


@app.route('/getLogs', methods=['GET'])
def get_logs():
    return render_template('getLogs.html', maxDate=latestLogDate, getLogs=True)


@app.route('/logsByDate', methods=['POST'])
def get_log_by_date():
    if request.method == 'POST':
        oneLogDate = request.form.get('oneLogDate', None)
        if(oneLogDate != None and oneLogDate != ''):
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            getLogByDateQuery = '''
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
            WHERE daily_logs.date = %s
            ;
            '''
            if not doesLogExistByDate(oneLogDate):
                return render_template("getLogs.html", missingMessage="A log for {} does not exist, either it was a rest day or was not logged".format(oneLogDate))
            val = (oneLogDate,)
            cursor.execute(getLogByDateQuery, val)
            oneDateLog = cursor.fetchall()
            oneDateLogMD = {'date': oneDateLog[0]['date'],
                            'name': oneDateLog[0]['routine_name'],
                            'type': oneDateLog[0]['type']
                            }

            return render_template('getLogs.html', maxDate=latestLogDate, oneDateLogMD=oneDateLogMD, oneDateLog=oneDateLog)

    return render_template('getLogs.html', maxDate=latestLogDate, getLogs=True, missingMessage=oneLogDate)


@app.route('/logsByNumber', methods=['POST'])
def get_n_recent_logs():
    if request.method == 'POST':
        numberOfLogsReq = request.form.get('numberOfLogs', None)
        if numberOfLogsReq == '':
            return render_template('getLogs.html', empty_val_n=True, maxDate=latestLogDate, getLogs=True)
        if numberOfLogsReq != None and numberOfLogsReq != '':
            queryForLastNroutineDateIds = '''
                SELECT routine_date_id
                FROM daily_logs
                ORDER BY date DESC
                LIMIT %s;
            '''
            val = (int(numberOfLogsReq),)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(queryForLastNroutineDateIds, val)
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
                where daily_logs.routine_date_id = %s
                ;
                '''
                val = (int(routineDateId),)
                cursor.execute(query, val)
                currLog = cursor.fetchall()
                currLogMD = {'date': currLog[0]['date'],
                             'name': currLog[0]['routine_name'],
                             'type': currLog[0]['type']
                             }
                nLogsMD.append(currLogMD)
                nLogs.append(currLog)

            return render_template('getLogs.html', maxDate=latestLogDate, nLogs=nLogs, nLogsMD=nLogsMD, n=len(nLogs))

    return render_template('getLogs.html', maxDate=latestLogDate)


@app.route('/logsByType', methods=['POST'])
def get_logs_by_type():
    routineName = request.form.get('routineName', None)
    routineType = request.form.get('routineType', None)
    if routineName == None:
        return render_template("getLogs.html", missingMessage="Routine Name cannot be empty")
    if routineType == None:
        return render_template("getLogs.html", missingMessage="Routine Type cannot be empty")
    routine = routineName + '-' + routineType
    routineId = routineNameIdMap[routine.lower()]
    latestIDQuery = '''
    select MAX(daily_logs.routine_date_id) from daily_logs where daily_logs.routine_id=%s;
    '''
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
                where daily_logs.routine_id = %s
                AND daily_logs.routine_date_id=%s
                ;
    '''
    valForRoutineId = (int(routineId),)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(latestIDQuery, valForRoutineId)
    latestRoutineDateID = cursor.fetchall(
    )[0]['MAX(daily_logs.routine_date_id)']
    valForLog = (int(routineId), int(latestRoutineDateID))
    cursor.execute(query, valForLog)
    typeLog = cursor.fetchall()
    typeLogMD = {'date': typeLog[0]['date'],
                 'name': typeLog[0]['routine_name'],
                 'type': typeLog[0]['type']
                 }
    return render_template('getLogs.html', typeLog=typeLog, typeLogMD=typeLogMD)


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        if 'username' not in request.form or request.form['username'] == '':
            return render_template('login.html', message='please enter a value for username\n')
        if 'password' not in request.form or request.form['password'] == '':
            return render_template('login.html', message='please enter a value for password\n')
        elif 'username' in request.form and 'password' in request.form:
            passwordHash = getPasswordHash(request.form['password'])
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            query = 'SELECT * FROM users WHERE username = %s'
            vals = (request.form['username'],)
            cursor.execute(query, vals)
            account = cursor.fetchone()
            if not account:
                message = 'User "{}" does not exist'.format(
                    request.form['username'])
            else:
                if(account['password'] != passwordHash):
                    return render_template('login.html', message='incorrect password for "{}"'.format(request.form['username']))
                session['loggedin'] = True
                session['id'] = account['user_id']
                session['username'] = account['username']
                return redirect(url_for('addLog'))
        return render_template('login.html', message=message)
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username", None)
        email = request.form.get("email", None)
        if len(username) > 20:
            return render_template("register.html", message="username too long")
        if doesUsernameExist(username):
            return render_template("register.html", message="username exists pick a different one")
        password = request.form.get("password", None)
        if(password == None or password == ''):
            return render_template("register.html", message="password needed")
        isValid, msg = validatePassword(password)
        if(isValid):
            passwordHash = getPasswordHash(password)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            query = '''
                INSERT INTO users(username,password,email) VALUES (%s,%s,%s)
            '''
            vals = (username, passwordHash, email)
            cursor.execute(query, vals)
            mysql.connection.commit()

            return render_template("register.html", success=True)

        return render_template("register.html", message=msg)
    return render_template("register.html")


@app.route('/addLog', methods=['GET', 'POST'])
def addLog():
    print(session)
    if not session.get("loggedin"):
        return redirect(url_for('login'))
    else:
        if request.method == 'GET':
            return render_template('addLog.html')

        elif request.method == 'POST':
            routineName = request.form.get('workout', None)
            routineType = request.form.get('type', None)
            logDate = request.form.get('logDate', None)
            if routineName == None or routineName == '':
                return render_template("addLog.html", missingMessage="Please add a routine name")
            if routineType == None or routineType == '':
                return render_template("addLog.html", missingMessage="Please add a routine type")
            routine = routineName + '-' + routineType
            routineId = routineNameIdMap[routine.lower()]
            query = "INSERT INTO daily_logs(date,routine_id) VALUES (%s, %s)"
            vals = (logDate, routineId)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(query, vals)
            args = [int(routineId), logDate]
            cursor.callproc('addRoutineExercisesToLogs', args)
            mysql.connection.commit()
            recentlyAddedLog = getLastAddedLog()

            return render_template("addLog.html", recentlyAddedLog=recentlyAddedLog, added=True)


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
        setRepWeights = []
        for i in range(counter):
            currSetVal = setRepWeightObj['sets'+str(i)]
            currRepVal = setRepWeightObj['reps'+str(i)]
            currWeightVal = setRepWeightObj['weight'+str(i)]
            setRepWeights.append((currSetVal, currRepVal, currWeightVal))

        for i in range(counter):
            vals = (setRepWeights[i][0], setRepWeights[i][1], setRepWeights[i][2],
                    latestLogId, r_d_e_id+i)

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(query, vals)
            mysql.connection.commit()
        success = True
        return render_template("addLog.html", success=success)


@ app.after_request
def after_request(response):
    return response


if __name__ == '__main__':
    app.run(debug=True)
