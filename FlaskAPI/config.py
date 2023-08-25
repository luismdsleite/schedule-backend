import os
import json
from datetime import timedelta


SETTINGS_FILE_NAME = 'settings.json'
CONF_DICT = {}


def load_configuration_from_json(_json_filepath = SETTINGS_FILE_NAME):
    """Load the configuration from the settings.json file"""
    global CONF_DICT
    try:
        with open(_json_filepath) as conf_file:
            CONF_DICT = json.load(conf_file)['config']

    except Exception as e:
        raise Exception(f'Failed to load {_json_filepath} due to: {e}')


class Config(object):
    """Common generic configurations"""
    ## Define the application directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    ## Load configuration details from settings.json file
    load_configuration_from_json(os.path.join(BASE_DIR, SETTINGS_FILE_NAME))

    ## HOST & PORT
    HOST = CONF_DICT['common']['HOST']
    PORT = CONF_DICT['common']['PORT']

    ## Version
    VERSION = CONF_DICT['common']['VERSION']

    ## URL Prefix
    URL_PREFIX = CONF_DICT['common']['URL_PREFIX']

    ## Statement for enabling the development environment
    DEBUG = CONF_DICT['common']['DEFAULT_DEBUG']

    ## Application threads
    THREADS_PER_PAGE = CONF_DICT['common']['THREADS_PER_PAGE']

    ## Enable protection against *Cross-site Request Forgery (CSRF)*
    CSRF_ENABLED = CONF_DICT['common']['CSRF_ENABLED']
    CSRF_SESSION_KEY = CONF_DICT['common']['CSRF_SESSION_KEY']


class ProductionConfig(Config):
    '''
    Configuration specific to production environment
    '''
    ENV = CONF_DICT['env']['production']['ENV']
    DEBUG = CONF_DICT['env']['production']['DEBUG']
    DEVELOPMENT = CONF_DICT['env']['production']['DEVELOPMENT']
    CONNECT_TIMEOUT = CONF_DICT['env']['production']['DATABASE_CONNECTION_OPTIONS']['CONNECT_TIMEOUT']
    JWT_SECRET_KEY = CONF_DICT['env']['production']['DATABASE_CONNECTION_OPTIONS']['JWT_SECRET_KEY']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(CONF_DICT['env']['production']['DATABASE_CONNECTION_OPTIONS']['JWT_ACCESS_TOKEN_EXPIRES']))  


class DevelopmentConfig(Config):
    '''
    Configuration specific to development environment
    '''
    ENV = CONF_DICT['env']['development']['ENV']
    DEBUG = CONF_DICT['env']['development']['DEBUG']
    DEVELOPMENT = CONF_DICT['env']['development']['DEVELOPMENT']
    DB_HOST = CONF_DICT['env']['development']['DATABASE_CONNECTION_OPTIONS']['DB_HOST']
    DB_PORT = CONF_DICT['env']['development']['DATABASE_CONNECTION_OPTIONS']['DB_PORT']
    DB_USER = CONF_DICT['env']['development']['DATABASE_CONNECTION_OPTIONS']['DB_USER']
    DB_PASSWD = CONF_DICT['env']['development']['DATABASE_CONNECTION_OPTIONS']['DB_PASSWD']
    DB_NAME = CONF_DICT['env']['development']['DATABASE_CONNECTION_OPTIONS']['DB_NAME']
    CONNECT_TIMEOUT = CONF_DICT['env']['development']['DATABASE_CONNECTION_OPTIONS']['CONNECT_TIMEOUT']
    PEPPER = CONF_DICT['env']['development']['DATABASE_CONNECTION_OPTIONS']['PEPPER']
    JWT_SECRET_KEY = CONF_DICT['env']['development']['DATABASE_CONNECTION_OPTIONS']['JWT_SECRET_KEY']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(CONF_DICT['env']['development']['DATABASE_CONNECTION_OPTIONS']['JWT_ACCESS_TOKEN_EXPIRES']))