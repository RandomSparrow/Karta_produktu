import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langchain.prompts import PromptTemplate
from logs.logger import logging
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func
from BackendOperations.database import session, Language, TextModel, Translation
from dotenv import load_dotenv

load_dotenv()
class Translations:
    def __init__(self, client):
        self.client = client

    def create_prompt(self, text, language):
        try:
            TEMPLATE = """Translate '{fraza}' into {jezyk}"""
            prompt_template = PromptTemplate(
                input_variables=['fraza', 'jezyk'],
                template=TEMPLATE
            )
            prompt = prompt_template.format(fraza=text, jezyk=language)
            logging.info("Prompt created successfully")
            return prompt
        except Exception as e:
            logging.error(f"Error creating prompt: {e}")
            raise

    def create_translation(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model= os.getenv('model'),
                messages=[
                    {
                        "role": "system",
                        "content": "You generate translations based on the learned language patterns. Input is always in Polish. If no appropriate translation is found, return 'BRAK TŁUMACZENIA'"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.1
            )
            logging.info("Translation created successfully")
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error creating translation: {e}")
            raise

    def database_translation(self, word, language):
        try:
            # Find the language ID
            try:
                language_obj = session.query(Language).filter(func.lower(Language.language_name) == language.lower()).one()
                language_id = language_obj.language_id
            except NoResultFound:
                logging.info("No language_id found for language")
                return None

            # Find the text ID
            try:
                text_obj = session.query(TextModel).filter(func.lower(TextModel.text) == word.lower()).one()
                text_id = text_obj.text_id
            except NoResultFound:
                logging.info("No text_id found for word")
                return None

            # Find the translation
            try:
                translation_obj = session.query(Translation).filter_by(text_id=text_id, language_id=language_id).one()
                logging.info("Database translation retrieved successfully")
                return translation_obj.translation_text
            except NoResultFound:
                logging.info("No translation found for text_id and language_id")
                return None

        except Exception as e:
            logging.error(f"Error retrieving database translation: {e}")
            raise