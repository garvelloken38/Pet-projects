-- Замена капитана

CREATE OR REPLACE PROCEDURE update_captain(
    ship INTEGER,
    new_cap VARCHAR(50),
    retire_date DATE DEFAULT CURRENT_DATE
)
LANGUAGE plpgsql
AS $$

DECLARE 
	old_cap VARCHAR(50);
	start_service DATE;
	end_service DATE;

BEGIN 
	SELECT captain INTO old_cap
	FROM ships 
	WHERE id = ship;

	IF NOT FOUND THEN RAISE EXCEPTION 'Корабль % не найден', ship;
	END IF;

	SELECT launched INTO start_service
	FROM ships
	WHERE id = ship;

	WITH sunk_ships AS (
	SELECT s.id, battle_end
	FROM ships s
	LEFT JOIN outcomes o ON s.id = o.ship
	LEFT JOIN battles b ON o.battle = b.id
	WHERE result = 'destroyed')
	
	SELECT battle_end INTO end_service
	FROM sunk_ships
	WHERE id = ship;

	IF retire_date < start_service OR (end_service IS NOT NULL AND retire_date > end_service) THEN
	RAISE EXCEPTION 'Новое назначение % либо раньше спуска на воду корабля, либо позде его гибели', retire_date;
	END IF;
	
	INSERT INTO captains_retired VALUES
	(old_cap, ship, retire_date);

	UPDATE ships
	SET captain = new_cap 
	WHERE id = ship;
END;
$$;

COMMENT ON PROCEDURE update_captain IS 'Меняет действующего капитана корабля и 
сохраняет историю изменений в отдельную таблицу';

