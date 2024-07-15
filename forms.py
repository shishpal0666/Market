from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from market import get_db_connection  # Import the get_db_connection function from market.py

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=30)])
    email_address = StringField('Email', validators=[DataRequired(), Email()])
    password1 = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Register')

    def validate_username(self, username_to_check):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE username = %s", (username_to_check.data,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user:
            raise ValidationError('Username already exists! Please try a different username.')

    def validate_email_address(self, email_address_to_check):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT email_address FROM users WHERE email_address = %s", (email_address_to_check.data,))
        email_address = cur.fetchone()
        cur.close()
        conn.close()
        if email_address:
            print("Email already exist")
            raise ValidationError('Email Address already exists! Please try a different email address.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign in')

class PurchaseItemForm(FlaskForm):
    submit=SubmitField('Purchase Item!')

class SellItemForm(FlaskForm):
    submit=SubmitField('Sell Item!')