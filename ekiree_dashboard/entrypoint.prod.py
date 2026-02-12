#!/app/bin/python
import subprocess
import sys
import time

PYTHON = "/app/bin/python"
GUNICORN = "/app/bin/gunicorn"


def wait_for_database():
    print("Waiting for database to be ready...")
    while True:
        result = subprocess.run(
            [PYTHON, "manage.py", "check", "--database", "default"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            break
        print("MySQL is unavailable - sleeping")
        time.sleep(3)
    print("MySQL is up - executing commands")


def run_migrations():
    subprocess.run([PYTHON, "manage.py", "migrate", "--noinput"], check=True)


def start_gunicorn():
    sys.exit(
        subprocess.call(
            [GUNICORN, "--bind", "0.0.0.0:8000", "--workers", "3", "poetfolio.wsgi:application"]
        )
    )


if __name__ == "__main__":
    wait_for_database()
    run_migrations()
    start_gunicorn()
