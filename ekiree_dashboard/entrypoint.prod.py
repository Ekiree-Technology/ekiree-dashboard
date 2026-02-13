#!/app/bin/python
import os
import subprocess
import time

import MySQLdb

PYTHON = "/app/bin/python"
GUNICORN = "/app/bin/gunicorn"


def wait_for_database():
    """Wait for the database to accept connections."""
    host = os.environ.get("POETFOLIO_DB_HOST", "localhost")
    user = os.environ.get("POETFOLIO_DB_USER", "poetfolio")
    password = os.environ.get("POETFOLIO_DB_PASSWORD", "")
    db_name = os.environ.get("POETFOLIO_DB_NAME", "poetfolio_dev")

    # If running with Docker secrets, read from /run/secrets/
    if os.environ.get("DOCKER_SECRETS") == "True":
        def read_secret(name, default=""):
            try:
                with open(f"/run/secrets/{name}") as f:
                    return f.read().strip()
            except IOError:
                return default

        host = read_secret("POETFOLIO_DB_HOST", host)
        user = read_secret("POETFOLIO_DB_USER", user)
        password = read_secret("POETFOLIO_DB_PASSWORD", password)
        db_name = read_secret("POETFOLIO_DB_NAME", db_name)

    print("Waiting for database to be ready...")
    while True:
        try:
            conn = MySQLdb.connect(host=host, user=user, passwd=password, db=db_name, port=3306)
            conn.close()
            break
        except MySQLdb.Error:
            print("MySQL is unavailable - sleeping")
            time.sleep(3)
    print("MySQL is up - executing commands")


def run_migrations():
    subprocess.run([PYTHON, "manage.py", "migrate", "--noinput"], check=True)


def start_gunicorn():
    os.execv(GUNICORN, [GUNICORN, "--bind", "0.0.0.0:8000", "--workers", "3", "poetfolio.wsgi:application"])


if __name__ == "__main__":
    wait_for_database()
    run_migrations()
    start_gunicorn()
