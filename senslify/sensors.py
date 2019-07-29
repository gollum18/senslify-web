import aiohttp, aiohttp_jinja2
import bson, pymongo, simplejson

from senslify.sockets import message


@aiohttp_jinja2.template('sensors/info.jinja2')
async def info_handler(request):
    '''
    Defines a POST endpoint for the sensor info page.
    Arguments:
        request: A aiohttp.web.Request object.
    '''
    # redirect to the sensors page if no sensor was provided
    if not request.query['sensor']:
        location = request.app.router['sensors'].url_for()
        raise aiohttp.web.HTTPFound(location=location)
    # build the WebSokcet address for the webpage
    prefix = 'wss://' if request.secure else 'ws://'
    sensor = request.query['sensor']
    host = request.app['config'].host
    port = ':' + request.app['config'].port
    # TODO: Remove the hard-coded dependency here
    route = '/ws'
    ws_url = prefix + host + port + route
    # build the sensor records page
    readings = []
    num_readings = request.app['config'].num_readings
    try:
        with request.app['db'].readings.find().limit(num_readings) as cursor:
            for reading in cursor:
                readings.append(reading)
    except pymongo.errors.ConnectionFailure as e:
        status = 403
        if request.app['config'].debug:
            text = 'HTTP RESPONSE 403:\n%s'.format(str(e))
        else:
            text = 'HTTP RESPONSE 403:\nUnable to connect to the senslify database!'
    except pymongo.errors.PyMongoError as e:
        status = 403
        if request.app['config'].debug:
            text = 'HTTP RESPONSE 403:\n%s'.format(str(e))
        else:
            text = 'HTTP RESPONSE 403:\nAn error has occurred with the database!'
    # build the response thru jinja2
    return {'title': 'Sensor Info',
            'sensor': sensor,
            'readings': readings,
            'num_readings': num_readings,
            'ws_url': ws_url}


def build_info_url(request, sensor):
    route = request.app.router['info'].url_for().with_query(
        {'sensor': sensor['sensor']}
    )
    return route
    

@aiohttp_jinja2.template('sensors/sensors.jinja2')
async def sensors_handler(request):
    '''
    Defines a GET endpoint for the sensors listing page.
    Arguments:
        request: A aiohttp.web.Request object.
    '''
    
    status = 200
    sensors = []
    try:
        # get the list of sensors
        with request.app['db'].senslify.sensors.find() as cursor:
            for sensor in cursor:
                sensor['url'] = build_info_url(request, sensor)
                sensors.append(sensor)
    except pymongo.errors.ConnectionFailure as e:
        status = 403
        if request.app['config'].debug:
            text = 'HTTP RESPONSE 403:\n%s'.format(str(e))
        else:
            text = 'HTTP RESPONSE 403:\nUnable to connect to the senslify database!'
    except pymongo.errors.PyMongoError as e:
        status = 403
        if request.app['config'].debug:
            text = 'HTTP RESPONSE 403:\n%s'.format(str(e))
        else:
            text = 'HTTP RESPONSE 403:\nAn error has occurred with the database!'
    if status != 200:
        return aiohttp.web.Response(text=text, status=status)
    else:
        return {'title': 'Sensors', 'sensors': sensors}


async def upload_handler(request):
    '''
    Defines a POST endpoint for uploading sensor data.
    Arguments:
        request: A aiohttp.web.Request object.
    '''
    status = 200
    text = 'Request processed successfully!'
    # It should be safe to insert the msg directly, but I still
    #   want to explicitly convert the msg to BSON for safety reasons
    json = simplejson.dumps(request.query['msg'])
    # TODO: Perform verification on the data passed to the handler
    if json['sensor'] is None:
        status = 400
        text = 'You must supply a sensor ID in your message.'
    if status == 200:
        # upload the received message to the database
        doc = bson.BSON.encode(json)
        try:
            await request.app['db'].insert_one(doc)
        except pymongo.errors.ConnectionFalure as e:
            status = 500
            if request.app['config'].debug:
                text = 'HTTP RESPONSE 500:\n%s'.format(str(e))
            else:
                text = 'HTTP RESPONSE 500:\nUnable to connect to the senslify database!'
        except pymongo.errors.PyMongoError as e:
            status = 500
            if request.app['config'].debug:
                text = 'HTTP RESPONSE 500:\n%s'.format(str(e))
            else:
                text = 'HTTP RESPONSE 500:\nAn error has occurred with the database!'
        # send the message to the room
        await message(json['sensor'], json)
    return aiohttp.web.Response(text=text, status=status)
