import aiohttp, aiohttp_jinja2, aiohttp_session
import bson, pymongo, simplejson


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
    # get the stuff needed to build the response
    host = request.app['config'].host
    protocol = 'wss://' if request.secure else 'ws://'
    sensor = request.query['sensor']
    # build the response thru jinja2
    return {'title': 'Sensor Info',
            'sensor': sensor,
            'ws_url': protocol + host + '/ws'}


def build_info_url(request, sensor):
    route = request.app.router['info'].url_for().with_query(
        {'sensor': sensor.sensor}
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
        # only retrieve the first 100 records, let the user get more
        #   if they need to - get the sensors in batches of 10
        # TODO: This needs optimized
        async with request.app['db'].sensors.find().batch_size(10) as cursor:
            async for sensor in cursor:
                sensor['url'] = build_info_url(request, sensor)
                sensors.append(sensor)
    except pymongo.errors.ConnectionFailure:
        status = 403
        text = 'Unable to connect to the senslify database!'
    except pymongo.errors.PyMongoError:
        status = 403
        text = 'An error has occurred with the database!'
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
    if json['sensor'] is None or json['group'] is None:
        status = 400
        text = 'You must supply both a sensor ID and a group ID.'
    if status == 200:
        doc = bson.BSON.encode(json)
        try:
            await request.app['db'].insert_one(doc)
        except pymongo.errors.ConnectionFalure:
            status = 500
            text = 'Unable to connect to the senslify database!'
        except pymongo.errors.PyMongoError:
            status = 500
            text = 'An error has occurred with the database!'
    return aiohttp.web.Response(text=text, status=status)
