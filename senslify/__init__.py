import asyncio
import aiohttp, aiohttp_jinja2, aiohttp_sse
import aiomongo
import config
import jinja2
import bson, simplejson

import queue, os


#
# TODO:
# - Still need to get the client to pass the sensor in its query string
# - Need to remove clients from the sensor listener list. Currently, this
#   process will be time consuming due to the way listeners are programmed.
#


#
# The following two endpoints enable data uploading and live streaming. They are
#   not meant to be visited directly from browser clients.
#


async def upload(request):
    '''
    Defines a POST endpoint for uploading data to the server.

    Data is expected to be in JSON format and passed in a request object
    named 'reading'.
    '''
    reading = simplejson.dumps(request.query_string['reading'])
    sensor = reading['sensor']
    # add the reading to the database
    #   must convert dumped json to bson as mongodb uses bson
    await request.app['db'].readings.insert_one(bson.loads(reading))
    # return a status message
    return aiohttp.Response(text='Reading uploaded successfully')


#
# The following endpoints define visitable pages for browser clients.
#


@aiohttp_jinja2.template('sensors/live.jinja2')
async def live(request):
    sensor = 0
    return {
        'title': 'Live on Sensor: ' + sensor,
        'ws_url': app['config'].ws_url
    }


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


#
# create the application and setup the file loader
#

app = aiohttp.web.Application()
loader=jinja2.FileSystemLoader(
        [os.path.join(os.path.dirname(__file__), "templates")],
        autoescape=jinja2.select_autoescape(['html', 'xml']))
aiohttp_jinja2.setup(app, loader=loader)

#
# setup the application configuration and any 'global' variables
#

# loads in the configuration file
app['config'] = config.Config('senslify.cfg')

# sets up the database
app['db'] = aiomongo.MongoClient(app['config'].dbconn)

# setup up the static root url for static content
app['static_root_url'] = '/static'

# register resources for the routes
app.router.add_resource(r'', name='index')
app.router.add_resource(r'/sensors/live', name='live')
app.router.add_resource(r'/sensors', name='sensors')

# register the routes for the application
app.router.add_route('POST', '/upload', upload)
app.router.add_route('GET', '/ws', poll_handler)
app.router.add_route('GET', '/sensors', sensors)
app.router.add_route('POST', '/sensors/live', live)
app.router.add_route('GET', '/', index)

# start the web server
aiohttp.web.run_app(app, host='0.0.0.0', port=app['config'].port)
