
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

import datetime as dt

from passlib.context import CryptContext

from sqlalchemy import (
    create_engine,
)

from jose import (
    jwt,
)

from dotenv import load_dotenv
import os

import pandas as pd

load_dotenv(".env",override=True)

# NOTE: This is the hashing strategy for user passwords, and the bear token expiration.
ACCESS_TOKEN_EXPIRE_MINUTES = 300
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

db_url = 'sqlite:///.data/sqlite.db'

app = Flask(__name__)

app.secret_key = SECRET_KEY

def check_logged_in():
    '''
    Checks the session for a bearer token.

    If found, it is decoded with the app's secret key.

    If the token is not expired, return True and the Username.

    If the token is expired, pop any tokens from the session.

    If not bearer or the token was popped as expired, return False and None.
    '''

    bearer = session.get('bearer')
    username=None
    expires=None
    
    if bearer:
        try:
            payload = jwt.decode(bearer, SECRET_KEY,algorithms=[ALGORITHM])
        except:
            return False, None
        username: str = payload.get("sub")
        expires = payload.get("exp")

        if dt.datetime.utcnow().timestamp()<expires:
            
            return True, username
        
        session.pop('bearer',None)
        
    return False, None


@app.route("/")
def index():

    logged_in, username=check_logged_in()

    return render_template('index.html',logged_in=logged_in,username=username)


@app.route("/register",methods=['GET','POST'])
def register():

    logged_in, username=check_logged_in()
    
    err_message = None

    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        hashed_password = pwd_context.hash(password)
        
        engine = create_engine(db_url,echo=False)
        conn=engine.connect()

        #check username exists
        unames = pd.read_sql(f"select username from users where lower(username) = '{username}';",con=conn)
        if len(unames)>0:
            err_message='Username already in database. Try logging in.'
            return render_template('register.html',err_message=err_message, logged_in=logged_in)
        else:

            record = pd.DataFrame({
                'username':[username],
                'password':[hashed_password]
            })
            record.to_sql('users',con=conn,if_exists='append',index=False)
            conn.commit()
            conn.close()
            engine.dispose()

            return redirect(url_for('login'))

    return render_template('register.html',err_message=err_message, logged_in=logged_in)


@app.route("/login",methods=['GET','POST'])
def login():
    logged_in, username=check_logged_in()

    err_message=None
    
    if request.method == 'POST':

        username = request.form['username'].lower()
        password = request.form['password']

        engine = create_engine(db_url,echo=False)
        conn=engine.connect()
        sql = f""" 
        select
        username,password
        from users
        where username = '{username}'
        """
        df = pd.read_sql(sql,con=conn)
        conn.close()
        engine.dispose()


        if len(df)==0:
            #NOTE: There was no such username in the database. Back to login
            err_message = 'Wrong username or password!'
            return render_template('login.html',err_message=err_message, logged_in=logged_in)
        
        check_password = df['password'].values[0]

        if not pwd_context.verify(password,check_password):
            #NOTE: The username is present, but the password didn't verify. Back to login
            err_message = 'Wrong username or password!'
            return render_template('login.html',err_message=err_message, logged_in=logged_in)
        
        #NOTE: User is password verified. Create a token, encoded by this app's key.
        #NOTE: jwt.decode cannot decode this token without the key. Doing so outside the app won't work.
        access_token_expires = dt.timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = (dt.datetime.utcnow() + access_token_expires).timestamp()
        to_encode = {'sub':username}
        to_encode.update({"exp": expire})
        access_token = jwt.encode(to_encode, 
                                SECRET_KEY,
                                algorithm=ALGORITHM)
        
        #NOTE: Set the bearer token as a session cookie. Return home page.
        session['bearer'] = access_token
        
        return redirect(url_for('index'))
    
    #NOTE: Non-POST request returns login.html.
    return render_template('login.html',err_message=err_message, logged_in=logged_in)


@app.route("/logout")
def logout():
    #NOTE: logout always returns you home. Pops bearer is it exists. 
    #NOTE: If no bearer, you are logged out. If user saves the bearer outside of browser,
    #NOTE: they could reset their own cookie, and if not expired, be logged back in.
    logged_in, username=check_logged_in()

    session.pop('bearer',None)

    return redirect(url_for('index'))
