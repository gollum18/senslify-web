import asyncio
import aiohttp, aiohttp_sse, aiohttp_jinja2
import jinja2

import os


async def upload(request):
    '''
    Defines a POST endpoint for uploading a data to the server.

    Data is expected to be in JSON format and be labelled as 'reading'.
    '''
    pass


@aiohttp_jinja2.template('sensors/live.jinja2')
async def live(request):
    return {'title': 'Title'}


@aiohttp_jinja2.template('sensors/sensors.jinja2')
async def sensors(request):
    '''
    Defines a GET endpoint for listing sensors.
    '''
    return {'title': 'Sensors'}


@aiohttp_jinja2.template('sensors/index.jinja2')
async def index(request):
    '''
    Defines a GET endpoint for the index page,
    '''
    return {'title': 'Index'}


# create the application and setup the file loader
app = aiohttp.web.Application()
loader=jinja2.FileSystemLoader(
        [os.path.join(os.path.dirname(__file__), "templates")])
app['static_root_url'] = '/static'
aiohttp_jinja2.setup(app, loader=loader)
# register resources for the routes
app.router.add_resource(r'', name='index')
app.router.add_resource(r'/sensors/live', name='live')
app.router.add_resource(r'/sensors', name='sensors')
# register the routes for the application
app.router.add_route('POST', '/upload', upload)
app.router.add_route('GET', '/sensors', sensors)
app.router.add_route('GET', '/sensors/live', live)
app.router.add_route('GET', '/', index)
# start the web server
aiohttp.web.run_app(app, host='0.0.0.0', port=8080)
