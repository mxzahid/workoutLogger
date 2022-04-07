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

SELECT * from routine_date_exercise;
SELECT * from daily_logs;

-- insert all exercises for routine w/ default reps
DELIMITER $$
CREATE PROCEDURE proc()
BEGIN

DECLARE counter INT;
DECLARE maxId INT;
DECLARE r_d_id INT;
DECLARE r_id INT;
SET r_id=4;
SET r_d_id=(SELECT daily_logs.routine_date_id FROM  daily_logs WHERE daily_logs.routine_id=r_id);

SET counter = (SELECT MIN(routine_exercises.routine_exercise_id) FROM routine_exercises where routine_id=r_id);
SET maxId=(SELECT MAX(routine_exercises.routine_exercise_id) FROM routine_exercises where routine_id=r_id);


WHILE(counter IS NOT NULL AND counter <= maxId)
DO
	INSERT INTO routine_date_exercise(routine_date_id,routine_exercise_id,sets,reps)
	VALUES (r_d_id,counter,(SELECT default_sets FROM routine_exercises where routine_exercise_id=counter),(SELECT default_reps FROM routine_exercises where routine_exercise_id=counter) );
	-- SELECT * from routine_exercises WHERE routine_exercise_id=counter;
    SET counter = counter+1;

END WHILE;
END$$
DELIMITER ;

CALL proc();

SELECT * from routine_date_exercise;
truncate routine_date_exercise;
DROP PROCEDURE proc;

DELIMITER ;

-- checks which attributes can be null or not null
SELECT COLUMN_NAME, COLUMN_KEY
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE table_name = 'routine_date_exercise';
  
-- sets, reps, weights can be null
	ALTER TABLE routine_date_exercise
    MODIFY COLUMN sets INT;

show tables;

CREATE TABLE routine_date_exercise(
	r_d_e_id INT AUTO_INCREMENT NOT NULL,
    routine_date_id INT NOT NULL,
    routine_exercise_id INT NOT NULL,
    sets INT,
    reps INT,
    weight INT,
    PRIMARY KEY (r_d_e_id),
    FOREIGN KEY (routine_date_id) REFERENCES daily_logs(routine_date_id),
    FOREIGN KEY (routine_exercise_id) REFERENCES routine_exercises(routine_exercise_id)
    );

SELECT routine_exercises.routine_exercise_id,routines.routine_id, routines.routine_name, 
		routines.type, exercises.exercise_id, exercises.name, routine_exercises.default_sets,
        routine_exercises.default_reps
FROM routine_exercises 
	JOIN routines
		ON routines.routine_id=routine_exercises.routine_id
	JOIN exercises 
		ON exercises.exercise_id=routine_exercises.exercise_id
	ORDER BY routine_exercise_id;
    
UPDATE routine_exercises SET default_sets=4, default_reps=12 WHERE routine_exercise_id=59;



UPDATE routine_date_exercise SET weight=35 where r_d_e_id=8;

SELECT daily_logs.date, routines.routine_name, routines.type, exercises.name, routine_date_exercise.sets, routine_date_exercise.reps, routine_date_exercise.weight FROM daily_logs JOIN routine_date_exercise ON routine_date_exercise.routine_date_id=daily_logs.routine_date_id JOIN routine_exercises ON routine_date_exercise.routine_exercise_id=routine_exercises.routine_exercise_id JOIN routines ON routine_exercises.routine_id=routines.routine_id JOIN exercises ON routine_exercises.exercise_id=exercises.exercise_id WHERE daily_logs.date = '2022-03-23' ;


        


