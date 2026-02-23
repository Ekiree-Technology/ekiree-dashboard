#!/app/bin/python
import argparse
import os
import subprocess
import time

import MySQLdb

PYTHON = "/app/bin/python"
GUNICORN = "/app/bin/gunicorn"

MIGRATION_CHECK_MAX_ATTEMPTS = int(os.environ.get("MIGRATION_CHECK_MAX_ATTEMPTS", "60"))
MIGRATION_CHECK_INTERVAL_SECONDS = int(os.environ.get("MIGRATION_CHECK_INTERVAL_SECONDS", "5"))


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


def wait_for_migrations():
    """Wait until migrations are fully applied."""
    print("Waiting for migrations to be applied...")
    for attempt in range(1, MIGRATION_CHECK_MAX_ATTEMPTS + 1):
        result = subprocess.run(
            [PYTHON, "manage.py", "migrate", "--check", "--noinput"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("Migrations are up to date")
            return

        if attempt == MIGRATION_CHECK_MAX_ATTEMPTS:
            print("Final migration check failed")
            print(f"Return code: {result.returncode}")
            if result.stdout.strip():
                print("migrate --check stdout:")
                print(result.stdout.strip())
            if result.stderr.strip():
                print("migrate --check stderr:")
                print(result.stderr.strip())

        print(
            "Migrations are not yet applied "
            f"(attempt {attempt}/{MIGRATION_CHECK_MAX_ATTEMPTS}) - sleeping"
        )
        time.sleep(MIGRATION_CHECK_INTERVAL_SECONDS)

    raise SystemExit(
        "Migrations were not applied within the expected time window. "
        "Refusing to start Gunicorn."
    )


def start_gunicorn():
    os.execv(GUNICORN, [GUNICORN, "--bind", "0.0.0.0:8000", "--workers", "3", "poetfolio.wsgi:application"])


def parse_args():
    parser = argparse.ArgumentParser(description="Dashboard production entrypoint")
    parser.add_argument("--migrate-only", action="store_true", help="Run migrations and exit")
    parser.add_argument("--skip-migrate", action="store_true", help="Skip migrations and only serve")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.migrate_only and args.skip_migrate:
        raise SystemExit("Cannot use --migrate-only and --skip-migrate together")

    wait_for_database()

    if args.migrate_only:
        print("Entrypoint mode: migrate-only")
        run_migrations()
        raise SystemExit(0)

    if args.skip_migrate:
        print("Entrypoint mode: skip-migrate")
        wait_for_migrations()
    else:
        print("Entrypoint mode: default (migrate + serve)")
        run_migrations()

    start_gunicorn()
