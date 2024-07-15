from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, UserMixin, logout_user, login_required, current_user
import psycopg2
from psycopg2.extras import RealDictCursor
from bcrypt import hashpw, gensalt, checkpw
import os

# Define Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Define database connection function
def get_db_connection():
    conn = psycopg2.connect(
        database="FlaskMarket",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )
    return conn

# Define User model
class User(UserMixin):
    def __init__(self, id, username, email_address, password_hash, budget=1000):
        self.id = id
        self.username = username
        self.email_address = email_address
        self.password_hash = password_hash
        self.budget = budget

    def check_password(self, password):
        return checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def can_purchase(self, item_obj):
        return self.budget >= item_obj['price']

    def can_sell(self, item_obj):
        return item_obj['owner'] == self.id

    @property
    def prettier_budget(self):
        if len(str(self.budget)) >= 4:
            return f'{str(self.budget)[:-3]},{str(self.budget)[-3:]}'
        else:
            return f"{self.budget}"

# Configure Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'loginpage'
login_manager.login_message_category = "info"

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE id = %s", (int(user_id),))
    user_data = cur.fetchone()
    cur.close()
    conn.close()
    if user_data:
        return User(
            id=user_data['id'],
            username=user_data['username'],
            email_address=user_data['email_address'],
            password_hash=user_data['password_hash'],
            budget=user_data.get('budget', 1000)  # Ensure default value if budget is not present
        )
    return None

# Routes

@app.route("/")
@app.route("/home")
def homepage():
    return render_template("home.html")

@app.route("/market", methods=['GET', 'POST'])
@login_required
def marketpage():
    from forms import PurchaseItemForm, SellItemForm
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == "POST":
        # Purchase Item
        purchased_item = request.form.get('purchased_item')
        if purchased_item:
            cur.execute("SELECT * FROM items WHERE name = %s", (purchased_item,))
            p_item_object = cur.fetchone()
            if p_item_object:
                if current_user.can_purchase(p_item_object):
                    cur.execute("UPDATE items SET owner = %s WHERE id = %s", (current_user.id, p_item_object['id']))
                    cur.execute("UPDATE users SET budget = budget - %s WHERE id = %s", (p_item_object['price'], current_user.id))
                    conn.commit()
                    current_user.budget -= p_item_object['price']
                    flash(f"Congratulations! You purchased {p_item_object['name']} for {p_item_object['price']}₹", category='success')
                else:
                    flash(f"Unfortunately, you don't have enough money to purchase {p_item_object['name']}!", category='danger')
        
        # Sell Item
        sold_item = request.form.get('sold_item')
        if sold_item:
            cur.execute("SELECT * FROM items WHERE name = %s", (sold_item,))
            s_item_object = cur.fetchone()
            if s_item_object:
                if current_user.can_sell(s_item_object):
                    cur.execute("UPDATE items SET owner = NULL WHERE id = %s", (s_item_object['id'],))
                    cur.execute("UPDATE users SET budget = budget + %s WHERE id = %s", (s_item_object['price'], current_user.id))
                    conn.commit()
                    current_user.budget += s_item_object['price']
                    flash(f"Congratulations! You sold {s_item_object['name']} back to market!", category='success')
                else:
                    flash(f"Something went wrong with selling {s_item_object['name']}", category='danger')

        return redirect(url_for('marketpage'))

    if request.method == "GET":
        cur.execute('SELECT * FROM items WHERE owner IS NULL')
        items = cur.fetchall()
        cur.execute('SELECT * FROM items WHERE owner = %s', (current_user.id,))
        owned_items = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('market.html', items=items, purchase_form=purchase_form, owned_items=owned_items, selling_form=selling_form)

@app.route('/register', methods=['GET', 'POST'])
def registerpage():
    from forms import RegisterForm  # Import inside the function to avoid circular import
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email_address = form.email_address.data
        password_hash = hashpw(form.password1.data.encode('utf-8'), gensalt()).decode('utf-8')

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        try:
            cur.execute(
                "INSERT INTO users (username, email_address, password_hash) VALUES (%s, %s, %s)",
                (username, email_address, password_hash)
            )
            conn.commit()
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            user_data = cur.fetchone()
            cur.close()
            conn.close()
            if user_data:
                user = User(
                    id=user_data['id'],
                    username=user_data['username'],
                    email_address=user_data['email_address'],
                    password_hash=user_data['password_hash'],
                    budget=user_data.get('budget', 1000)  # Ensure default value if budget is not present
                )
                login_user(user)
                flash(f"Account created successfully! You are now logged in as {user.username}", category='success')
                return redirect(url_for('marketpage'))
            else:
                flash('User creation failed, please try again.', category='danger')
        except Exception as e:
            print(f'There was an error with creating a user: {e}')
            conn.rollback()
            cur.close()
            conn.close()
            flash(f'There was an error with creating a user: {e}', category='danger')
    if form.errors != {}:  # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def loginpage():
    from forms import LoginForm  # Import inside the function to avoid circular import
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cur.fetchone()
        cur.close()
        conn.close()

        if user_data and checkpw(password.encode('utf-8'), user_data['password_hash'].encode('utf-8')):
            user = User(user_data['id'], user_data['username'], user_data['email_address'], user_data['password_hash'], user_data['budget'])
            login_user(user)
            flash(f'Success! You are logged in as: {user.username}', category='success')
            return redirect(url_for('marketpage'))
        else:
            flash('Username and password do not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for('homepage'))

if __name__ == "__main__":
    app.run(debug=True)
