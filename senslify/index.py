# THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
# APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
# HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT
# WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
# PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE
# DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR
# CORRECTION.

# Name: index.py
# Since: Aug. 20th, 2019
# Author: Christen Ford
# Purpose: Defines handlers for the index page.

import aiohttp, aiohttp_jinja2


def build_sensors_url(request, group):
    """Helper function that creates a url for a given group.
    
    Args:
        request (aiohttp.web.Request): The request that initiated the connection to the homepage.
        group (int): Group information on one group from the database.
    """
    route = request.app.router['sensors'].url_for().with_query(
        {'groupid': group['groupid']}
    )
    return route


@aiohttp_jinja2.template('sensors/index.jinja2')
async def index_handler(request):
    """Defines a GET endpoint for the index page.
    
    Args:
        request (aiohttp.web.Request): An aiohttp.Request object.
    """
    status = 200
    groups = []
    try:
        # get the group information from the database
        async for group in request.app['db'].get_groups():
            group['url'] = build_sensors_url(request, group)
            groups.append(group)
    except Exception as e:
        status = 403
        if request.app['config'].debug:
            text = 'HTTP RESPONSE 403:\n{}'.format(str(e))
        else:
            text = 'HTTP RESPONSE 403\n An error has occurred with the database!'
    if status != 200:
        return aiohttp.web.Response(text=text, status=status)
    else:
        return {'title': 'Home', 'groups': groups}
