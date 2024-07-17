import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from glob import glob
from openai import OpenAI
from BackendOperations.export_operations import ExportOperations
from BackendOperations.translations import Translations
from BackendOperations.import_operations import ImportOperations
from logs.logger import logging

def create_body(translation):
    try:
        body = {
            "Number": translation[3],
            "Usecase": translation[4],
            "Product": translation[0],
            "System": translation[1],
            "Standard": translation[5],
            "Declared performance": translation[6],
            "Signature date": translation[2]
        }
        logging.info("JSON body created successfully")
        return body
    except Exception as e:
        logging.error(f"Error creating JSON body: {e}")
        raise

def export_document_data(src):
    try:
        doc_op = ExportOperations(src)
        to_translate, template = doc_op.export_data()
        logging.info("Document data exported successfully")
        return to_translate, template
    except Exception as e:
        logging.error(f"Error exporting document data: {e}")
        raise

def initialize_translation_instance(api_key):
    try:
        client = OpenAI(api_key=api_key)
        instance = Translations(client)
        logging.info("Translation instance initialized successfully")
        return instance
    except Exception as e:
        logging.error(f"Error initializing translation instance: {e}")
        raise

def process_language_translations(instance, to_translate, template, language):
    try:
        translated_template = template[:]

        # Process main data
        for word in to_translate[:2]:
            translated = instance.database_translation(word, language)
            if translated is not None:
                translated_template.append(translated)
            else:
                prompt = instance.create_prompt(word, language)
                translated = instance.create_translation(prompt)
                translated_template.append(f"{translated} [AI]")

        # Process characteristics
        translated_characteristics = []
        for table in to_translate[2:]:
            table_translations = []
            for characteristic in table:
                    translated = instance.database_translation(characteristic, language)
                    if translated is not None:
                        table_translations.append(translated)
                    else:
                        prompt = instance.create_prompt(characteristic, language)
                        translated = instance.create_translation(prompt)
                        table_translations.append(f"{translated} [AI]")
            translated_characteristics.append(table_translations)

        translated_template.append(translated_characteristics)

        logging.info("Language translations processed successfully")
        return translated_template
    except Exception as e:
        logging.error(f"Error processing language translations: {e}")
        raise

def transform_data(data):
    try:
        # Extract the base elements and the characteristics list
        base_elements = data[:6]
        characteristics_lists = data[6]

        # Transform each sublist in characteristics_lists to a list of dictionaries
        transformed_characteristics = []
        for sublist in characteristics_lists:
            transformed_sublist = []
            for i in range(0, len(sublist), 2):
                characteristic = {'Essential characteristic': sublist[i], 'Performance': sublist[i + 1]}
                transformed_sublist.append(characteristic)
            transformed_characteristics.append(transformed_sublist)

        # Combine the base elements with the transformed characteristics list
        transformed_data = base_elements + [transformed_characteristics]

        logging.info("Data transformed successfully")
        return transformed_data
    except Exception as e:
        logging.error(f"Error transforming data: {e}")
        raise

def import_translated_data(language, template, empty, sign, save_path):
    try:
        body = create_body(template)
        Import = ImportOperations(body)

        if language == "English":
            Import.import_data({empty[0]:"EN", empty[1]:"UK"}, save_path)
            empty = empty[2:]
        else:
            Import.import_data({empty[0]:sign}, save_path)
            empty = empty[1:]

        logging.info("Translated data imported successfully")
        return empty
    except Exception as e:
        logging.error(f"Error importing translated data: {e}")
        raise

def main(src, save_path):
    try:
        empty = glob("BackendOperations\\Templates/*")
        
        # Export data from document
        to_translate, template = export_document_data(src)

        # Languages for translation
        languages = {"English":"EN", "Czech":"CZ", "German":"DE", "Lithuanian":"LT", "Latvian":"LV", "Slovak":"SK"}
        # API Key for OpenAI
        Key = "sk-proj-8DNPgF5srINl2NQC86PjT3BlbkFJpKCv2ZACt7guVImVhtij"
        instance = initialize_translation_instance(Key)
        
        # Process translations and import data for each language
        for language, sign in languages.items():
            translated_template = process_language_translations(instance, to_translate, template, language)
            transformed_data = transform_data(translated_template)
            empty = import_translated_data(language, transformed_data, empty, sign, save_path)

        logging.info("Process completed successfully")
    except Exception as e:
        logging.error(f"Error in process: {e}")
        raise
