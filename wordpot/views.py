#!/usr/bin/env python

from flask import request, render_template, redirect, url_for, abort
from wordpot import app, pm
from wordpot.helpers import *
from wordpot.logger import LOGGER

import psycopg2
import datetime

TEMPLATE = app.config['THEME'] + '.html'

@app.route('/', methods=['GET', 'POST'])
@app.route('/<filename>.<ext>', methods=['GET', 'POST'])
def commons(filename=None, ext=None):

    if app.config['POSTGRESQL_ENABLED']:
        cursor = app.config['postgresql_dbh'].cursor()
        cursor.execute("INSERT INTO connections (source_ip, source_port, dest_host, dest_port, user_agent, url, method, path, headers, timestamp) VALUES ('%s',%s,'%s',%s,'%s','%s','%s','%s','%s','%s')" % (request.remote_addr, request.environ['REMOTE_PORT'], request.environ['SERVER_NAME'], request.environ['SERVER_PORT'], request.user_agent.string, request.url, request.method, request.path, str(request.headers), str(datetime.datetime.now())))
        app.config['postgresql_dbh'].commit()

    # Plugins hook
    for p in pm.hook('commons'):
        p.start(filename=filename, ext=ext, request=request)
        if 'log' in p.outputs:
            LOGGER.info(p.outputs['log'])
        if 'log_json' in p.outputs and app.config['HPFEEDS_ENABLED']:
            app.config['hpfeeds_client'].publish(app.config['HPFEEDS_TOPIC'], p.outputs['log_json'])
        if 'log_postgresql' in p.outputs and app.config['POSTGRESQL_ENABLED']:
            try:
                cursor = app.config['postgresql_dbh'].cursor()
                cursor.execute(p.outputs['log_postgresql'])
                app.config['postgresql_dbh'].commit()
            except Exception as e:
                print(e)
        if 'template' in p.outputs:
            if 'template_vars' in p.outputs:
                return render_template(p.outputs['template'], vars=p.outputs['template_vars'])
            return render_template(p.outputs['template'], vars={})
   
    if filename is None and ext is None:
        return render_template(TEMPLATE, vars={})
    elif filename == 'index' and ext == 'php':
        return render_template(TEMPLATE, vars={})
    else:        
        abort(404)

@app.route('/wp-admin', methods=['GET', 'POST'])
@app.route('/wp-admin<regex("\/.*"):subpath>', methods=['GET', 'POST'])
def admin(subpath='/'):
    """ Admin panel probing handler """
    origin = request.remote_addr
    LOGGER.info('%s probed for the admin panel with path: %s', origin, subpath)
    
    if app.config['POSTGRESQL_ENABLED']:
        cursor = app.config['postgresql_dbh'].cursor()
        cursor.execute("INSERT INTO connections (source_ip, source_port, dest_host, dest_port, user_agent, url, method, path, headers, timestamp) VALUES ('%s',%s,'%s',%s,'%s','%s','%s','%s','%s','%s')" % (request.remote_addr, request.environ['REMOTE_PORT'], request.environ['SERVER_NAME'], request.environ['SERVER_PORT'], request.user_agent.string, request.url, request.method, request.path, str(request.headers), str(datetime.datetime.now())))
        app.config['postgresql_dbh'].commit()

    # Plugins hook
    for p in pm.hook('plugins'):
        p.start(subpath=subpath, request=request)
        if 'log' in p.outputs:
            LOGGER.info(p.outputs['log'])
        if 'log_json' in p.outputs and app.config['HPFEEDS_ENABLED']:
            app.config['hpfeeds_client'].publish(app.config['HPFEEDS_TOPIC'], p.outputs['log_json'])
        if 'log_postgresql' in p.outputs and app.config['POSTGRESQL_ENABLED']:
            try:
                cursor = app.config['postgresql_dbh'].cursor()
                cursor.execute(p.outputs['log_postgresql'])
                app.config['postgresql_dbh'].commit()
            except Exception as e:
                print(e)
        if 'template' in p.outputs:
            if 'template_vars' in p.outputs:
                return render_template(p.outputs['template'], vars=p.outputs['template_vars'])
            return render_template(p.outputs['template'], vars={})
    
    return redirect('wp-login.php')

@app.route('/wp-content/plugins/<plugin>', methods=['GET', 'POST'])
@app.route('/wp-content/plugins/<plugin><regex("(\/.*)"):subpath>', methods=['GET', 'POST'])
def plugin(plugin, subpath='/'):
    """ Plugin probing handler """
    origin = request.remote_addr
    LOGGER.info('%s probed for plugin "%s" with path: %s', origin, plugin, subpath)
    
    if app.config['POSTGRESQL_ENABLED']:
        cursor = app.config['postgresql_dbh'].cursor()
        cursor.execute("INSERT INTO connections (source_ip, source_port, dest_host, dest_port, user_agent, url, method, path, headers, timestamp) VALUES ('%s',%s,'%s',%s,'%s','%s','%s','%s','%s','%s')" % (request.remote_addr, request.environ['REMOTE_PORT'], request.environ['SERVER_NAME'], request.environ['SERVER_PORT'], request.user_agent.string, request.url, request.method, request.path, str(request.headers), str(datetime.datetime.now())))
        app.config['postgresql_dbh'].commit()

    # Is the plugin in the whitelist?
    if not is_plugin_whitelisted(plugin):
        abort(404)

    # Plugins hook
    for p in pm.hook('plugins'):
        p.start(plugin=plugin, subpath=subpath, request=request)
        if 'log' in p.outputs:
            LOGGER.info(p.outputs['log'])
        if 'log_json' in p.outputs and app.config['HPFEEDS_ENABLED']:
            app.config['hpfeeds_client'].publish(app.config['HPFEEDS_TOPIC'], p.outputs['log_json'])
        if 'log_postgresql' in p.outputs and app.config['POSTGRESQL_ENABLED']:
            try:
                cursor = app.config['postgresql_dbh'].cursor()
                cursor.execute(p.outputs['log_postgresql'])
                app.config['postgresql_dbh'].commit()
            except Exception as e:
                print(e)
        if 'template' in p.outputs:
            if 'template_vars' in p.outputs:
                return render_template(p.outputs['template'], vars=p.outputs['template_vars'])
            return render_template(p.outputs['template'], vars={})

    return render_template(TEMPLATE, vars={})

@app.route('/wp-content/themes/<theme>', methods=['GET', 'POST'])
@app.route('/wp-content/themes/<theme><regex("(\/.*)"):subpath>', methods=['GET', 'POST'])
def theme(theme, subpath='/'):
    """ Theme probing handler """
    origin = request.remote_addr
    LOGGER.info('%s probed for theme "%s" with path: %s', origin, theme, subpath)

    if app.config['POSTGRESQL_ENABLED']:
        cursor = app.config['postgresql_dbh'].cursor()
        cursor.execute("INSERT INTO connections (source_ip, source_port, dest_host, dest_port, user_agent, url, method, path, headers, timestamp) VALUES ('%s',%s,'%s',%s,'%s','%s','%s','%s','%s','%s')" % (request.remote_addr, request.environ['REMOTE_PORT'], request.environ['SERVER_NAME'], request.environ['SERVER_PORT'], request.user_agent.string, request.url, request.method, request.path, str(request.headers), str(datetime.datetime.now())))
        app.config['postgresql_dbh'].commit()

    # Is the theme whitelisted?
    if not is_theme_whitelisted(theme):
        abort(404)

    # Plugins hook
    for p in pm.hook('themes'):
        p.start(theme=theme, subpath=subpath, request=request)
        if 'log' in p.outputs:
            LOGGER.info(p.outputs['log'])
        if 'log_json' in p.outputs and app.config['HPFEEDS_ENABLED']:
            app.config['hpfeeds_client'].publish(app.config['HPFEEDS_TOPIC'], p.outputs['log_json'])
        if 'log_postgresql' in p.outputs and app.config['POSTGRESQL_ENABLED']:
            try:
                cursor = app.config['postgresql_dbh'].cursor()
                cursor.execute(p.outputs['log_postgresql'])
                app.config['postgresql_dbh'].commit()
            except Exception as e:
                print(e)
        if 'template' in p.outputs:
            if 'template_vars' in p.outputs:
                return render_template(p.outputs['template'], vars=p.outputs['template_vars'])
            return render_template(p.outputs['template'], vars={})

    return render_template(TEMPLATE, vars={}) 

@app.route('/<path:path>', methods=['GET', 'POST'])
def connection(path='/'):

    if app.config['POSTGRESQL_ENABLED']:
        cursor = app.config['postgresql_dbh'].cursor()
        cursor.execute("INSERT INTO connections (source_ip, source_port, dest_host, dest_port, user_agent, url, method, path, headers, timestamp) VALUES ('%s',%s,'%s',%s,'%s','%s','%s','%s','%s','%s')" % (request.remote_addr, request.environ['REMOTE_PORT'], request.environ['SERVER_NAME'], request.environ['SERVER_PORT'], request.user_agent.string, request.url, request.method, request.path, str(request.headers), str(datetime.datetime.now())))
        app.config['postgresql_dbh'].commit()

    abort(404)

