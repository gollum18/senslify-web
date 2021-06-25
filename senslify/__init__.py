# THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
# APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
# HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT
# WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
# PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE
# DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR
# CORRECTION.

# Name: __init__.py
# Since: ~Jun 30th, 2019
# Author: Christen Ford
# Description: Serves as the entry point into the Senslify web application.
#   Contains a factory function to setup and configure the application
#   as well as a way to launch the application.


# monkey patch everything ahead of time
from gevent import monkey
monkey.patch_all()

import asyncio, getpass, os, sys
import aiohttp, aiohttp_jinja2, jinja2
import config, simplejson

# change the Provider import here if you want to use different one
#   You'll need to change it below too where I have marked
from senslify.db import database_shutdown_handler, MongoProvider
from senslify.errors import DBError, traceback_str

# import the various route handlers
from senslify.index import index_handler
from senslify.rest import rest_handler
from senslify.sensors import (
    info_handler, provision_handler, sensors_handler, upload_handler
)
from senslify.sockets import (
    socket_shutdown_handler, ws_handler
)

# import the filters module, import filters on an as needed basis
import senslify.filters


def get_local_ip():
    """Gets the local IP address of the host running the server."""

    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def build_app(config_file='./senslify/config/senslify.conf'):
    """ Factory function that creates a new instance of the server with
    the given configuration.

    Args:
    config_file (str): The path to the configuration file to use with the
    server (default ./senslify.conf)
    """
    # create the application and setup the file loader
    print('Configuring jinja2 template engine...')
    app = aiohttp.web.Application()
    loader=jinja2.FileSystemLoader(
        [os.path.join(os.path.dirname(__file__), "templates")]
    )

    # setup any filters for the application to use
    filters = {
        "date": senslify.filters.filter_date, # YYYY-MM-DD date format
        "datetime": senslify.filters.filter_datetime, # i18n datetime filter
        "simplejson_dumps": simplejson.dumps,
        "rstring": senslify.filters.filter_reading # custom reading filter
    }

    # setup the root url for static content like js/css
    app['static_root_url'] = '/static'

    # setup the application
    aiohttp_jinja2.setup(app, loader=loader, filters=filters)

    # setup the application configuration and any global variables
    print('Loading config file...')
    app['config'] = config.Config(config_file)

    # setup the database connection
    print('Initializing database connection...')
    # change the provider here if you want to use a different provider
    try:
        username = None
        password = None
        auth_required = input('Do we require a username and password to connect to the database server? [y|n]: ').lower()
        if auth_required == 'y':
            username = input('Username: ')
            password = getpass.getpass()
        app['db'] = MongoProvider(
            conn_str=app['config'].conn_str,
            username=username,
            password=password
        )
        username = None
        password = None
        app['db'].open()
        app['db'].init()
    except DBError as e:
        if app['config'].debug:
            print(traceback_str(e))
        else:
            print('ERROR: Unable to connect to the MongoDB instance, cannot continue!')
        sys.exit(-1)

    # setup the ws rooms
    app['rooms'] = dict()

    # register resources for the routes
    app.router.add_resource(r'/', name='index')
    app.router.add_resource(r'/sensors', name='sensors')
    app.router.add_resource(r'/sensors/info', name='info')
    app.router.add_resource(r'/ws', name='ws')
    app.router.add_resource(r'/rest', name='rest')

    # register the routes themselves
    app.router.add_route('GET', '/', index_handler)
    app.router.add_route('GET', '/sensors', sensors_handler)
    app.router.add_route('GET', '/sensors/info', info_handler)
    app.router.add_route('GET', '/sensors/provision', provision_handler)
    app.router.add_route('POST', '/sensors/upload', upload_handler)
    app.router.add_route('GET', '/ws', ws_handler)
    app.router.add_route('GET', '/rest', rest_handler)

    # register any shutdown handlers
    app.on_shutdown.append(database_shutdown_handler)
    app.on_shutdown.append(socket_shutdown_handler)

    # return the application
    return app


def main():
    """Entry point for the server. You may optionally supply a path to
    a configuration file to use with the server.
    """

    # get the app
    if len(sys.argv) == 2:
        app = build_app(config_file=sys.argv[2])
    else:
        app = build_app()
    # launch the web app
    aiohttp.web.run_app(app, host=get_local_ip(), port=app['config'].port)


if __name__ == '__main__':
    main()
