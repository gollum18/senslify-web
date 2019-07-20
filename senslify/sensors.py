import aiohttp_jinja2


@aiohttp_jinja2.template('sensors/info.jinja2')
async def info_handler(request):
    '''
    Defines a POST endpoint for the sensor info page.
    Arguments:
        request: A aiohttp.web.Request object.
    '''
    # get the stuff needed to build the response
    host = request.app['config'].host
    protocol = 'wss://' if request.secure else 'ws://'
    sensor = request.query['sensor']
    # build the response thru jinja2
    return {'title': 'Sensor Info',
            'sensor': sensor,
            'ws_url': protocol + host + '/ws'}


@aiohttp_jinja2.template('sensors/sensors.jinja2')
async def sensors_handler(request):
    '''
    Defines a GET endpoint for the sensors listing page.
    Arguments:
        request: A aiohttp.web.Request object.
    '''
    # TODO: The information on this page needs caching,
    #   it will take a long time to load otherwise
    return {'title': 'Sensors'}


async def upload_handler(request):
    '''
    Defines a POST endpoint for uploading sensor data.
    Arguments:
        request: A aiohttp.web.Request object.
    '''
    pass
