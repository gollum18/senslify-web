# monkey patch everything ahead of time
from gevent import monkey
monkey.patch_all()

import asyncio, os, sys
import aiohttp, aiohttp_jinja2, jinja2
import config

from senslify.db import MongoDBConn
from senslify.index import index_handler
from senslify.sensors import info_handler, sensors_handler, upload_handler
from senslify.sockets import ws_handler


def build_app(config_file=
    os.path.join(
        os.path.dirname(
            os.path.realpath(__file__)), 'senslify.conf')):
    '''
    Defines a factory function for creating the senslify web application.
    Arguments:
        config_file: The path to the senslify configuration file.
    Returns:
        An instance of the senslify web application configured with the
        settings found in the config_file.
    '''
    # create the application and setup the file loader
    app = aiohttp.web.Application()
    loader=jinja2.FileSystemLoader(
        [os.path.join(os.path.dirname(__file__), "templates")]
    )
    aiohttp_jinja2.setup(app, loader=loader)

    # setup the application configuration and any global variables
    app['config'] = config.Config(config_file)

    # setup the root url for static content like js/css
    app['static_root_url'] = '/static'
    
    # get the database connection
    app['db'] = MongoDBConn(conn_str=app['config'].conn_str)

    # register resources for the routes
    app.router.add_resource(r'/', name='index')
    app.router.add_resource(r'/sensors', name='sensors')
    app.router.add_resource(r'/sensors/info', name='info')
    app.router.add_resource(r'/ws', name='ws')

    # register the routes themselves
    app.router.add_route('GET', '/', index_handler)
    app.router.add_route('GET', '/sensors', sensors_handler)
    app.router.add_route('GET', '/sensors/info', info_handler)
    app.router.add_route('POST', '/sensors/upload', upload_handler)
    app.router.add_route('GET', '/ws', ws_handler)

    # return the application
    return app


def main():
    '''
    Defines the main entry point of the program.

    Installing senslify through setup.py will register the 'senslify-start-server'
    command. Invoking the 'senslify-start-server' command from the terminal or
    command line will invoke this command and start the server.
    '''
    # get the app
    if len(sys.argv) == 2:
        app = build_app(config_file=sys.argv[2])
    else:
        app = build_app()
    # launch the web app
    aiohttp.web.run_app(app, host=app['config'].host, port=app['config'].port)


if __name__ == '__main__':
    main()
