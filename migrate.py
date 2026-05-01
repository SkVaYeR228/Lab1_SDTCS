import argparse

import pymysql


def run_migration(db_host, db_user, db_password, db_name):

    try:

        conn = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)

        cursor = conn.cursor()

        cursor.execute("""

        CREATE TABLE IF NOT EXISTS items (

            id INT AUTO_INCREMENT PRIMARY KEY,

            name VARCHAR(255) NOT NULL,

            quantity INT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )

        """)

        conn.commit()

        print("Міграцію успішно завершено: таблицю items створено.")

    except Exception as e:

        print(f"Помилка міграції: {e}")

    finally:

        if 'conn' in locals() and conn.open:

            conn.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Скрипт міграції БД")

    parser.add_argument('--db-host', default='127.0.0.1')

    parser.add_argument('--db-user', required=True)

    parser.add_argument('--db-pass', required=True)

    parser.add_argument('--db-name', required=True)

    

    args = parser.parse_args()

    run_migration(args.db_host, args.db_user, args.db_pass, args.db_name)
