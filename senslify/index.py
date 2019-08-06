import aiohttp_jinja2
import pymongo


def build_sensors_url(request, group):
    '''
    Helper function that creates a url for a given group.
    Arguments:
        request: The request that initiated the connection to the homepage.
        group: Group information on one group from the database.
    '''
    route = request.app.router['sensors'].url_for().with_query(
        {'group': group['group']}
    )
    return route


@aiohttp_jinja2.template('sensors/index.jinja2')
async def index_handler(request):
    '''
    Defines a GET endpoint for the index page.
    Arguments:
        request: An aiohttp.Request object.
    '''
    status = 200
    groups = []
    try:
        # get the group information from the database
        with request.app['db'].senslify.groups.find() as cursor:
            for group in cursor:
                group['url'] = build_sensors_url(request, url)
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
