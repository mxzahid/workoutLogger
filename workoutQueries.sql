USE workoutlogs;

show tables;

select * from daily_logs 
JOIN routines 
	ON daily_logs.routine_id=routines.routine_id
JOIN  routine_exercises
	ON routine_exercises.routine_id=routines.routine_id
JOIN exercises 
	ON routine_exercises.exercise_id=exercises.exercise_id
JOIN routine_date_exercise
	ON routine_date_exercise.routine_exercise_id=exercises.exercise_id
;

-- get all routines with exercise names
SELECT routines.routine_name, routines.type, exercises.name from routine_exercises
JOIN exercises
	ON routine_exercises.exercise_id=exercises.exercise_id
JOIN routines
	ON routines.routine_id=routine_exercises.routine_id
;

-- get logs with names, routine, exercise, sets, reps
select daily_logs.date, 
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
;
