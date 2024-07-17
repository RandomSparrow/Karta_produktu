from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from Frontend_operations.db_models import User

class RegisterForm(FlaskForm):

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Ten adres e-mail jest już wykorzystywany! Spróbuj użyć innego')
        
    name = StringField(label='Imię:', validators=[Length(min=2, max=30), DataRequired()])
    lastname = StringField(label='Nazwisko:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='E-mail:', validators=[Email(), DataRequired()])
    password = PasswordField(label='Hasło:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Potwierdź hasło:', validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Stwórz konto')


class LoginForm(FlaskForm):
    email = StringField(label='E-mail:', validators=[DataRequired()])
    password = PasswordField(label='Hasło:', validators=[DataRequired()])
    submit = SubmitField(label='Zaloguj się')