from Frontend_operations.configure import db, bcrypt, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Text(db.Model):
    __tablename__ = 'texts'
    text_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Text {self.text_id}>'

class Translation(db.Model):
    __tablename__ = 'translations'
    translation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text_id = db.Column(db.Integer, db.ForeignKey('texts.text_id'), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('languages.language_id'), nullable=False)
    translation_text = db.Column(db.Text, nullable=False)

    text = db.relationship('Text', backref=db.backref('translations', lazy=True))
    language = db.relationship('Language', backref=db.backref('translations', lazy=True))

    __table_args__ = (db.UniqueConstraint('text_id', 'language_id', name='uix_text_language'),)

    def __repr__(self):
        return f'<Translation {self.translation_id}>'

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    role = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def hash_password(self):
        return self.hash_password

    @hash_password.setter
    def hash_password(self, plain_text_hash_password):
        self.password = bcrypt.generate_password_hash(plain_text_hash_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password, attempted_password)

class Language(db.Model):
    __tablename__ = 'languages'
    language_id = db.Column(db.Integer, primary_key=True)
    language_name = db.Column(db.String(255), nullable=False, unique=True)

    def __repr__(self):
        return f'<Language {self.language_name}>'
    
class History(db.Model):
    __tablename__ = 'translations_history'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    file = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'