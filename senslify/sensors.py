import aiohttp_jinja2


@aiohttp_jinja2.template('sensors/info.jinja2')
def info_handler(request):
    '''
    Defines a GET endpoint for the sensor info page.
    Arguments:
        request: A aiohttp.web.Request object.
    '''
    pass


@aiohttp_jinja2.template('sensors/sensors.jinja2')
def sensors_handler(request):
    '''
    Defines a GET endpoint for the sensors listing page.
    Arguments:
        request: A aiohttp.web.Request object.
    '''
    pass


def upload_handler(request):
    '''
    Defines a POST endpoint for uploading sensor data.
    Arguments:
        request: A aiohttp.web.Request object.
    '''
    pass
