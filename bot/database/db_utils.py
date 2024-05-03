import os
import logging
import psycopg2
from dotenv import load_dotenv


load_dotenv()

pool = None


async def start_db():
    connect_to_db()
    create_task_table()
    create_task_status_table()


async def close_db():
    disconnect()


def connect_to_db() -> None:
    global pool
    db_name = os.getenv("DATABASE_NAME")
    db_user = os.getenv("DATABASE_USER")
    db_pass = os.getenv("DATABASE_PASSWORD")
    db_host = os.getenv("DATABASE_HOST")
    db_port = os.getenv("DATABASE_PORT")

    try:
        pool = psycopg2.connect(
            user=db_user,
            password=db_pass,
            database=db_name,
            host=db_host,
            port=db_port
        )
        logging.info("Connected to db")

        cursor = pool.cursor()

        cursor.execute(
            "SELECT version()"
        )

    except Exception as e:
        logging.error(f"Error connecting to db: {e}")


def create_task_table() -> None:
    try:
        cursor = pool.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            task TEXT NOT NULL,
            description TEXT NOT NULL,
            task_num INTEGER NOT NULL,
            UNIQUE (user_id, task_num)
            )   
        ''')

        cursor.execute('''
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.triggers
                WHERE trigger_name = 'add_default_task_status_trigger'
            )    
        ''')
        trigger_exists = cursor.fetchone()[0]

        if not trigger_exists:

            cursor.execute('''
                CREATE OR REPLACE FUNCTION add_default_task_status()
                RETURNS TRIGGER AS $$
                BEGIN
                    INSERT INTO task_status (task_id, task_st) VALUES (NEW.id, 'not done');
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            ''')

            cursor.execute('''
                CREATE TRIGGER add_default_task_status_trigger
                AFTER INSERT ON tasks
                FOR EACH ROW
                EXECUTE FUNCTION add_default_task_status();
            ''')

        pool.commit()
        logging.info("Task table created successfully")
    except Exception as e:
        logging.error(f"Error creating task table: {e}")


def add_task_to_db(user_id: int, task: str, description: str) -> None:
    try:
        cursor = pool.cursor()

        cursor.execute('''
            SELECT COALESCE(MAX(task_num), 0) FROM tasks WHERE user_id = %s
        ''', (user_id,))

        max_task_num = cursor.fetchone()[0]

        task_num = max_task_num + 1

        cursor.execute('''
            INSERT INTO tasks (user_id, task, description, task_num) VALUES (%s, %s, %s, %s)
            ''',
            (user_id, task, description, task_num)
        )

        pool.commit()
        logging.info("Task added to database successfully")

    except Exception as e:
        logging.error(f"Error adding task to database: {e}")


def get_task(user_id: int) -> str:
    try:
        cursor = pool.cursor()
        cursor.execute('''
            SELECT task, description, id FROM tasks WHERE user_id = %s'''
            ,(user_id,)
        )
        tasks = cursor.fetchall()
        return tasks
    except Exception as e:
        logging.error(f"Error getting task from database: {e}")


def remove_task_from_db(user_id: int, task_num: int) -> None:
    try:
        cursor = pool.cursor()

        cursor.execute('''
                SELECT id, task_num FROM tasks WHERE user_id = %s AND task_num = %s
        ''', (user_id, task_num))

        tasks_id = cursor.fetchone()

        if tasks_id:

            cursor.execute('''
                DELETE FROM task_status WHERE task_id = %s
            ''', (tasks_id[0],))

            cursor.execute('''
                DELETE FROM tasks WHERE  id = %s AND task_num = %s
            ''', (tasks_id[0], tasks_id[1]))

            cursor.execute('''
                    UPDATE tasks SET task_num = task_num - 1 WHERE user_id = %s AND task_num > %s
            ''', (user_id, task_num))


            pool.commit()
            logging.info("Task removed from database successfully")
    except Exception as e:
        logging.error(f"Error removing task from database: {e}")


def create_task_status_table() -> None:
    try:
        cursor = pool.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_status (
            task_id integer references tasks(id),
            task_st TEXT NOT NULL
            )
        ''')

        pool.commit()
        logging.info("Task status table created successfully")
    except Exception as e:
        logging.error(f"Error creating task status: {e}")


def get_task_status(task_id: int) -> str:
    try:
        cursor = pool.cursor()
        cursor.execute('''
            SELECT task_st FROM task_status WHERE task_id = %s''', (task_id,)
        )
        task_st = cursor.fetchone()
        return task_st
    except Exception as e:
        logging.error(f"Error getting task status: {e}")


def mark_task_done(user_id: int, task_num: int) -> None:
    try:
        cursor = pool.cursor()
        cursor.execute('''
            SELECT id FROM tasks WHERE user_id = %s AND task_num = %s''', (user_id, task_num)
        )

        tasks_id = cursor.fetchone()

        if tasks_id:
            cursor.execute('''
                UPDATE task_status SET task_st = 'done' WHERE task_id = %s''', (tasks_id,))

            pool.commit()
            logging.info("Task removed from database successfully")
    except Exception as e:
        logging.error(f"Error marking task in database: {e}")


def disconnect():
    pool.close()
    logging.info("Connection to the database closed successfully")
