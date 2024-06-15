# Minimalist Flask Auth Template

This is a template that I use as a basis for other projects. It creates a flask app that allows the user to:

1. Register a username and password
2. Log in as a registered user
3. Renders different content on /index.html based on whether the user is logged in
4. Pop the session cookie in order to log out

The session cookie includes encrypted informtion, including the user's username and the time limit after which the session should expire. 

This uses sqlalchemy for database interactions. The db_url can be abstracted into the environment, or composed from a username and password in order to connect to a more secure/scalable database. This template creates a sqlite.db database locally. 

## Setup and Run

Installing dependencies:

```
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
mkdir .data
```

Creating the users table is the job of scripts/create_tbl.py, reading and executing the sql statement in sql/dql/create_users_tbl.sql:

```
python scripts/create_tbl.py
```

Running the app with the development server:

```
flask run
```