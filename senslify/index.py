import aiohttp, aiohttp_jinja2
import pymongo


def build_sensors_url(request, group):
    """Helper function that creates a url for a given group.
    
    Keyword arguments:
    request -- The request that initiated the connection to the homepage.
    group -- Group information on one group from the database.
    """
    route = request.app.router['sensors'].url_for().with_query(
        {'groupid': group['groupid']}
    )
    return route


@aiohttp_jinja2.template('sensors/index.jinja2')
async def index_handler(request):
    """Defines a GET endpoint for the index page.
    
    Keyword arguments:
    request -- An aiohttp.Request object.
    """
    status = 200
    groups = []
    try:
        # get the group information from the database
        async for group in request.app['db'].get_groups():
            group['url'] = build_sensors_url(request, group)
            groups.append(group)
    except pymongo.errors.ConnectionFailure as e:
        status = 403
        if request.app['config'].debug:
            text = 'HTTP RESPONSE 403:\n{}'.format(str(e))
        else:
            text = 'HTTP RESPONSE 403\nUnable to connect to the senslify database!'
    except pymongo.errors.PyMongoError as e:
        status = 403
        if request.app['config'].debug:
            text = 'HTTP RESPONSE 403:\n{}'.format(str(e))
        else:
            text = 'HTTP RESPONSE 403\n An error has occurred with the database!'
    if status != 200:
        return aiohttp.web.Response(text=text, status=status)
    else:
        return {'title': 'Home', 'groups': groups}
