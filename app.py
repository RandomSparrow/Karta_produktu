from Frontend_operations.configure import app
from logs.logger import logging

if __name__ == '__main__':
    try:
        app.run(debug=True)
        logging.info("Flask application started successfully.")
    except Exception as e:
        logging.error(f"Error starting the Flask application: {e}")
        raise