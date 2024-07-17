from flask import render_template, request, send_file, redirect, url_for, flash, jsonify
import os
from werkzeug.utils import secure_filename
from glob import glob
import zipfile
import io
from datetime import date
from Frontend_operations.forms import RegisterForm, LoginForm
from Frontend_operations.db_models import Text, Translation, User, Language, History
from Frontend_operations.configure import db, app
from flask_login import login_user, logout_user, current_user, login_required

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from BackendOperations.main import main
from logs.logger import logging

# Upewnij się, że foldery istnieją
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

@app.route('/translate', methods=['GET', 'POST'])
@login_required
def home_page():
    if request.method == 'POST':
        try:
            # Sprawdzenie, czy plik został wysłany
            if 'file' not in request.files:
                return 'No file part'
            file = request.files['file']
            if file.filename == '':
                return 'No selected file'
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Przetwarzanie pliku DOCX
                main(file_path, app.config['GENERATED_FOLDER'])
                os.remove(file_path)
                upload_path = app.config['GENERATED_FOLDER']
                files = glob(f'{upload_path}/*')
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for file in files:
                        arcname = os.path.basename(file)
                        zip_file.write(file, arcname)
                
                zip_buffer.seek(0)
                
                response = send_file(
                    zip_buffer,
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name='generated_files.zip'
                )

                for file in files:
                    os.remove(file)
                
                today = date.today()
                formated = today.strftime('%d.%m.%Y')
                
                new_record = History(name=current_user.name, lastname=current_user.lastname, date=formated, file=filename)
                db.session.add(new_record)
                db.session.commit()

                logging.info("Files processed and sent successfully.")
                return response
        except Exception as e:
            logging.error(f"Error during file processing: {e}")
            flash(f"Error during file processing: {e}", 'danger')
            return render_template('upload.html')

    return render_template('translate.html', active_page='home_page')

@app.route('/history')
@login_required
def history_page():
    items = History.query.all()
    return render_template('history.html', items=items, active_page='history_page')

@app.route('/database')
@login_required
def database_page():
    items = db.session.query(
        Translation.translation_id,
        Text.text,
        Language.language_name,
        Translation.translation_text
    ).join(Text, Translation.text_id == Text.text_id
    ).join(Language, Translation.language_id == Language.language_id).all()

    languages = Language.query.all()

    return render_template('database.html', items=items, languages=languages, active_page='database_page')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user_to_create = User(name=form.name.data, email_address=form.email_address.data, password=form.password.data)
            db.session.add(user_to_create)
            db.session.commit()
            login_user(user_to_create)
            flash('Account created successfully! You are now logged in as {}'.format(user_to_create.name), category='success')
            logging.info(f"New user registered: {form.email_address.data}")
            return redirect(url_for('home_page'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating user: {e}")
            flash('Error creating account. Please try again.', category='danger')
    if form.errors:
        for err_msg in form.errors.values():
            flash('There was an error with creating a user: {}'.format(err_msg), category='danger')
            logging.warning(f"Error in user registration form: {err_msg}")
    return render_template('register.html', form=form)

@app.route('/', methods=['GET', 'POST'])
def loging_page():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            attempted_user = User.query.filter_by(email=form.email.data).first()
            if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
                login_user(attempted_user)
                flash(f'Success! You are logged in as: {attempted_user.name} {attempted_user.lastname}', category='success')
                logging.info(f"User logged in: {form.email.data}")
                return redirect(url_for('home_page'))
            else:
                flash('Username and password are not match! Please try again.', category='danger')
                logging.warning(f"Failed login attempt for user: {form.email.data}")
        except Exception as e:
            logging.error(f"Error during login: {e}")
            flash('Error during login. Please try again.', category='danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out!', category='info')
    logging.info("User logged out.")
    return redirect(url_for('loging_page'))

@app.route('/update_translation/<int:id>', methods=['PATCH'])
@login_required
def update_translation(id):
    data = request.get_json()
    translation = Translation.query.get_or_404(id)
    text_record = Text.query.get(translation.text_id)
    
    text_record.text = data['text']
    translation.translation_text = data['translation']

    try:
        db.session.commit()
        return jsonify({'message': 'Translation updated successfully'}), 200
    except:
        db.session.rollback()
        return jsonify({'message': 'Error updating translation'}), 500

@app.route('/delete_translation/<int:id>', methods=['DELETE'])
@login_required
def delete_translation(id):
    translation = Translation.query.get_or_404(id)
    text_record = Text.query.get(translation.text_id)

    try:
        db.session.delete(translation)
        db.session.commit()
        return jsonify({'message': 'Translation deleted successfully'}), 200
    except:
        db.session.rollback()
        return jsonify({'message': 'Error deleting translation'}), 500

@app.route('/add_translation', methods=['POST'])
@login_required
def add_translation():
    try:
        data = request.get_json()
        
        # Check if language exists
        language_record = Language.query.filter_by(language_name=data['language']).first()
        if not language_record:
            logging.warning(f"Language not found: {data['language']}")
            return jsonify({'message': 'Language does not exist'}), 400

        # Check if text exists
        text_record = Text.query.filter_by(text=data['text']).first()
        if text_record is None:
            # Find max text_id and create a new entry if it does not exist
            max_text_id = db.session.query(db.func.max(Text.text_id)).scalar()
            new_text_id = max_text_id + 1 if max_text_id is not None else 1

            text_record = Text(text_id=new_text_id, text=data['text'])
            db.session.add(text_record)
            db.session.commit()  # Commit to get the text_id
        else:
            new_text_id = text_record.text_id

        # Check if translation for this text in the given language already exists
        existing_translation = Translation.query.filter_by(
            text_id=new_text_id,
            language_id=language_record.language_id
        ).first()

        if existing_translation:
            logging.warning("Translation for this text and language already exists.")
            return jsonify({'message': 'Translation for this text and language already exists'}), 400

        max_translation_id = db.session.query(db.func.max(Translation.translation_id)).scalar()
        new_translation_id = max_translation_id + 1 if max_translation_id is not None else 1

        new_translation = Translation(
            translation_id=new_translation_id,
            text_id=new_text_id,
            language_id=language_record.language_id,
            translation_text=data['translation']
        )

        db.session.add(new_translation)

        try:
            db.session.commit()
            logging.info(f"Translation added successfully for text_id {new_text_id} in language {language_record.language_name}.")
            return jsonify({'message': 'Translation added successfully'}), 201
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding translation: {e}")
            return jsonify({'message': 'Error adding translation', 'error': str(e)}), 500

    except Exception as e:
        logging.error(f"Error processing translation request: {e}")
        return jsonify({'message': 'Error processing request', 'error': str(e)}), 500


    