from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
import psycopg2
from werkzeug.security import generate_password_hash

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=30)])
    email_address = StringField('Email', validators=[DataRequired(), Email()])
    password1 = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Register')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.conn = psycopg2.connect(
            database="FlaskMarket", 
            user="postgres",
            password="password",
            host="localhost",
            port="5432"
        )

    def __del__(self):
        if hasattr(self, 'conn') and self.conn is not None:
            self.conn.close()

    def validate_username(self, username_to_check):
        cur = self.conn.cursor()
        cur.execute("SELECT username FROM users WHERE username = %s", (username_to_check.data,))
        user = cur.fetchone()
        cur.close()
        
        if user:
            raise ValidationError('Username already exists! Please try a different username.')

    def validate_email_address(self, email_address_to_check):
        cur = self.conn.cursor()
        cur.execute("SELECT email_address FROM users WHERE email_address = %s", (email_address_to_check.data,))
        email_address = cur.fetchone()
        cur.close()
        
        if email_address:
            raise ValidationError('Email Address already exists! Please try a different email address.')

    def create_user(self):
        hashed_password = generate_password_hash(self.password1.data, method='sha256')

        cur = self.conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, email_address, password_hash) VALUES (%s, %s, %s)",
                (self.username.data, self.email_address.data, hashed_password)
            )
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

        # Optionally, return user data or perform additional operations
        return True  # Return True or appropriate response as needed
