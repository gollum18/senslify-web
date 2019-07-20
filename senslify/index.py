import aiohttp_jinja2


@aiohttp_jinja2.template('sensors/index.jinja2')
async def index_handler(request):
    '''
    Defines a GET endpoint for the index page.
    Arguments:
        request: An aiohttp.Request object.
    '''
    return {'title': 'Home'}
