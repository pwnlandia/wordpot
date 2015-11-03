#/usr/bin/env python

try:
    from flask import Flask
except ImportError:
    print "\n[X] Please install Flask:"
    print "   $ pip install flask\n"
    exit()

from optparse import OptionParser
from wordpot.logger import *
from werkzeug.routing import BaseConverter
from wordpot.plugins_manager import PluginsManager
import os

# ---------------
# Regex Converter
# ---------------

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

# -------
# Options
# -------

REQUIRED_OPTIONS = {
        'HOST':  '127.0.0.1',
        'PORT':  '80',
        'THEME': 'twentyeleven',
        'BLOGTITLE': 'Random Rambling',
        'AUTHORS': ['admin']
        }


def parse_options():
    usage = "usage: %prog [options]"

    parser = OptionParser(usage=usage)
    parser.add_option('--host', dest='HOST', help='Host address')
    parser.add_option('--port', dest='PORT', help='Port number')
    parser.add_option('--title', dest='BLOGTITLE', help='Blog title')
    parser.add_option('--theme', dest='THEME', help='Default theme name')
    parser.add_option('--plugins', dest='PLUGINS', help='Fake installed plugins')
    parser.add_option('--themes', dest='THEMES', help='Fake installed themes')
    parser.add_option('--ver', dest='VERSION', help='Wordpress version')
    parser.add_option('--server', dest='SERVER', help='Custom "Server" header')

    (options, args) = parser.parse_args()
    
    for opt, val in options.__dict__.iteritems():
        if val is not None:
            if opt in ['PLUGINS', 'THEMES']:
                val = [ v.strip() for v in val.split(',') ] 
            app.config[opt] = val


def check_options():
    for k, v in REQUIRED_OPTIONS.iteritems():
        if k not in app.config:
            LOGGER.error('%s was not set. Falling back to default: %s', k, v)
            app.config[k] = v

# -------------------
# Building the Logger
# -------------------

logging_setup()

# ------------
# Building app
# ------------

app = Flask('wordpot')
app.url_map.converters['regex'] = RegexConverter

# Import config from file
conffile = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../wordpot.conf')
LOGGER.info('Loading conf file: %s', conffile)
try:
    app.config.from_pyfile(conffile)
except:
    LOGGER.error('Can\'t load conf file')
check_options()

if app.config['HPFEEDS_ENABLED']:
    import hpfeeds
    print 'Connecting to hpfeeds broker {}:{}'.format(app.config['HPFEEDS_HOST'], app.config['HPFEEDS_PORT'])
    app.config['hpfeeds_client'] = hpfeeds.new(
        app.config['HPFEEDS_HOST'], 
        app.config['HPFEEDS_PORT'], 
        app.config['HPFEEDS_IDENT'], 
        app.config['HPFEEDS_SECRET']
    )
    app.config['hpfeeds_client'].s.settimeout(0.01)
else:
    LOGGER.warn('hpfeeds is disabled')

if app.config['POSTGRESQL_ENABLED']:
    import psycopg2
    print 'Connecting to postgresql {}:{}'.format(app.config['POSTGRESQL_HOST'], app.config['POSTGRESQL_PORT'])
    app.config['postgresql_dbh'] = psycopg2.connect(database=app.config['POSTGRESQL_DATABASE'], user=app.config['POSTGRESQL_USER'], password=app.config['POSTGRESQL_PASSWORD'], host=app.config['POSTGRESQL_HOST'], port=app.config['POSTGRESQL_PORT'])
    cursor = app.config['postgresql_dbh'].cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS 
			login_attempts	(
				id SERIAL PRIMARY KEY,
				plugin TEXT, 
				source_ip TEXT, 
				source_port INTEGER,
				dest_host TEXT,  
				dest_port INTEGER, 
				username TEXT, 
				password TEXT, 
				user_agent TEXT, 
				url TEXT,
				timestamp TIMESTAMP
    );""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS 
			login_page_probes	(
				id SERIAL PRIMARY KEY,
				plugin TEXT, 
				source_ip TEXT, 
				source_port INTEGER,
				dest_host TEXT,  
				dest_port INTEGER, 
				user_agent TEXT, 
				url TEXT,
				timestamp TIMESTAMP
    );""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS 
			file_probes	(
				id SERIAL PRIMARY KEY,
				plugin TEXT,
				source_ip TEXT, 
				source_port INTEGER,
				dest_host TEXT,  
				dest_port INTEGER, 
				probed_filename TEXT,  
				user_agent TEXT, 
				url TEXT,
				timestamp TIMESTAMP
    );""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS 
			plugins_probes	(
				id SERIAL PRIMARY KEY,
				plugin TEXT,
				source_ip TEXT, 
				source_port INTEGER,
				dest_host TEXT,  
				dest_port INTEGER, 
				probed_plugin TEXT,  
				path TEXT,
				user_agent TEXT, 
				url TEXT,
				timestamp TIMESTAMP
    );""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS 
			themes_probes	(
				id SERIAL PRIMARY KEY,
				plugin TEXT,
				source_ip TEXT, 
				source_port INTEGER,
				dest_host TEXT,  
				dest_port INTEGER, 
				probed_theme TEXT, 
				path TEXT, 
				user_agent TEXT, 
				url TEXT,
				timestamp TIMESTAMP
    );""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS 
			author_probes	(
				id SERIAL PRIMARY KEY,
				plugin TEXT,
				source_ip TEXT, 
				source_port INTEGER,
				dest_host TEXT,  
				dest_port INTEGER, 
				probed_author TEXT,  
				user_agent TEXT, 
				url TEXT,
				timestamp TIMESTAMP
    );""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS 
			connections	(
				id SERIAL PRIMARY KEY,
				source_ip TEXT, 
				source_port INTEGER,
				dest_host TEXT,  
				dest_port INTEGER, 
				user_agent TEXT, 
				url TEXT,
				method TEXT,
				path TEXT,
				headers TEXT,
				timestamp TIMESTAMP
    );""")
    app.config['postgresql_dbh'].commit()
else:
    LOGGER.warn('postgresql is disabled')


# ------------------------
# Add Custom Server Header
#-------------------------

@app.after_request
def add_server_header(response):
    if app.config['SERVER']:
        response.headers['Server'] = app.config['SERVER']

    return response

# ----------------------------
# Building the plugins manager
# ----------------------------

pm = PluginsManager()
pm.load()

import wordpot.views
