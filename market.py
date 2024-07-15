from flask import Flask, render_template, redirect, url_for,flash
from forms import RegisterForm
import psycopg2
from psycopg2.extras import RealDictCursor
from bcrypt import hashpw, gensalt
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) 

def get_db_connection():
    conn = psycopg2.connect(
        database="FlaskMarket", 
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )
    return conn

@app.route("/")
@app.route("/home")
def homepage():
    return render_template("home.html")

@app.route("/market")
def marketpage():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM items')
    items = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('market.html', items=items)

@app.route('/register', methods=['GET', 'POST'])
def registerpage():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email_address = form.email_address.data
        password_hash = hashpw(form.password1.data.encode('utf-8'), gensalt()).decode('utf-8')

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (username, email_address, password_hash) VALUES (%s, %s, %s)",
                (username, email_address, password_hash)
            )
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('marketpage'))
        except Exception as e:
            print(f'There was an error with creating a user: {e}')
            conn.rollback()
            cur.close()
            conn.close()

    if form.errors != {}:  # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}',category='danger')

    return render_template('register.html', form=form)

if __name__ == "__main__":
    app.run(debug=True)
