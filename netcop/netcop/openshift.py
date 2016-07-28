import os

# directorio donde esta el proyecto
DJ_PROJECT_DIR = os.path.dirname(__file__)
# directorio donde se hace deploy del codigo. se borra el contenido
REPO_DIR = os.environ.get('OPENSHIFT_REPO_DIR', '')
# directorio donde se guarda archivos que necesitan ser persistidos.
# no se borran
DATA_DIR = os.environ.get('OPENSHIFT_DATA_DIR', '')
# directorio base donde esta el proyecyo
BASE_DIR = os.path.dirname(DJ_PROJECT_DIR)
# directorio de logs
LOG_DIR = os.environ.get('OPENSHIFT_LOG_DIR', '')

# dominios en los que el sitio funciona. sirve para prevenir ataques
ALLOWED_HOSTS = ['.rhcloud.com', '.netcop.ftp.sh']
DEBUG=False

POSTGRE_USERNAME = os.environ.get('OPENSHIFT_POSTGRESQL_DB_USERNAME', '')
POSTGRE_PASSWORD = os.environ.get('OPENSHIFT_POSTGRESQL_DB_PASSWORD', '')
POSTGRE_HOST = os.environ.get('OPENSHIFT_POSTGRESQL_DB_HOST', '')
POSTGRE_PORT = os.environ.get('OPENSHIFT_POSTGRESQL_DB_PORT', '')
POSTGRE_DB = os.environ.get('PGDATABASE', '')

SECRET_KEY = os.environ.get('OPENSHIFT_SECRET_TOKEN', '')


# base de datos productiva
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': POSTGRE_DB,
        'USER': POSTGRE_USERNAME,
        'PASSWORD': POSTGRE_PASSWORD,
        'HOST': POSTGRE_HOST,
        'PORT': POSTGRE_PORT,
    }
}


# lugar fisico donde se copiaran los archivos estaticos
STATIC_ROOT = os.path.join(REPO_DIR, 'wsgi', 'static')
# lugar fisico donde se copiaran los archivos que suban los usuarios
MEDIA_ROOT = os.path.join(DATA_DIR, 'media')
