# THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
# APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
# HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT
# WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
# PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE
# DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR
# CORRECTION.

# Name: sensors.py
# Since: ~Jul 28th, 2019
# Author: Christen Ford
# Description: Handles routes intended for the /sensors base route.

import aiohttp, aiohttp_jinja2, asyncio
import simplejson

from datetime import datetime

from senslify.errors import generate_error, traceback_str
from senslify.filters import filter_reading
from senslify.sockets import message
from senslify.verify import verify_reading


@aiohttp_jinja2.template('sensors/info.jinja2')
async def info_handler(request):
    """Defines a POST endpoint for the sensor info page.

    Arguments:
        request (aiohttp.web.Request): An aiohttp.web.Request object.

    Returns:
        (aiohttp.web.Response): An aiohttp.web.Response object.
    """
    # redirect to the sensors page if no sensor was provided
    if 'sensorid' not in request.query or 'groupid' not in request.query:
        raise aiohttp.web.HTTPFound(location=request.app.router['sensors'].url_for())

    # build the WebSocket address for the webpage
    prefix = 'wss://' if request.secure else 'ws://'
    sensorid = 0
    groupid = 0
    rtypeid = 0
    try:
        sensorid = int(request.query['sensorid'])
        groupid = int(request.query['groupid'])
        rtypeid = int(request.app['config'].default_rtypeid)
    except Exception as e:
        if request.app['config'].debug:
            return generate_error(traceback_str(e), 403)
        else:
            return generate_error('ERROR: Malformed request!', 403)
    host = request.host
    route = '/ws'
    ws_url = prefix + host + route

    # build the sensor readings query
    # TODO: There has to be a way where I don't have to save these to memory
    rtypes = None
    try:
        rtypes = [i async for i in request.app['db'].get_rtypes()]
    except Exception as e:
        if request.app['config'].debug:
            return generate_error(traceback_str(e), 403)
        else:
            return generate_error('ERROR: An error has occurred with the database!', 403)
    num_readings = int(request.app['config'].num_readings)

    # get the time span
    end = datetime.timestamp(datetime.now())
    start = datetime.timestamp(datetime.today().replace(day=1))

    # build the response thru jinja2
    if not rtypes:
        return generate_error("ERROR: No rtypes found in the database!", 403)
    else:
        return {
            'title': 'Sensor Info',
            'sensorid': sensorid,
            'groupid': groupid,
            'rtypeid': rtypeid,
            'rtypes': rtypes,
            'num_readings': num_readings,
            'ws_url': ws_url,
            'start_date': start,
            'end_date': end
        }


def build_info_url(request, sensor):
    """Helper function that creates a url for a given sensor.

    This function is called primarily by the sensors_handler function to
    generate links to the sensor info page.

    Keyword arguments:
    request -- The request that wants the sensor url.
    sensor -- The sensor to generate a url for.
    """
    route = request.app.router['info'].url_for().with_query(
        {
            'sensorid': sensor['sensorid'],
            'groupid': sensor['groupid']
        }
    )
    return route


@aiohttp_jinja2.template('sensors/sensors.jinja2')
async def sensors_handler(request):
    """Defines a GET endpoint for the sensors listing page.

    Keyword arguments:
    request -- A aiohttp.web.Request object.
    """
    # redirect to the index page if no group was provided
    if 'groupid' not in request.query:
        raise aiohttp.web.HTTPFound(location=request.app.router['index'].url_for())
    group = -1
    sensors = []
    try:
        group = int(request.query['groupid'])
        async for sensor in request.app['db'].get_sensors(group):
            sensor['url'] = build_info_url(request, sensor)
            sensors.append(sensor)
    except Exception as e:
        if request.app['config'].debug:
            return generate_error(traceback_str(e), 403)
        else:
            return generate_error('ERROR: An error has occurred with the database!', 403)
    # return the response through jinja2
    if not sensors:
        return generate_error("ERROR: No sensors found for given group!", 403)
    else:
        return {
            'title': 'Sensors for group {g}:'.format(g=group),
            'sensors': sensors
        }


async def upload_handler(request):
    """Defines a POST endpoint for uploading sensor data.

    Keyword arguments:
    request -- A aiohttp.web.Request object.
    """
    doc = simplejson.loads(await request.text())
    # TODO: Perform verification on the data passed to the handler
    try:
        # Only insert if reading verifies as true
        if verify_reading(doc):
            # insert the reading into the database
            await request.app['db'].insert_reading(doc)
            # generate the string version of the message for output on page
            doc['rstring'] = filter_reading(doc)
            # send the message to the room
            await message(request.app['rooms'], doc['sensorid'], doc)
    except Exception as e:
        if request.app['config'].debug:
            return generate_error(traceback_str(e), 403)
        else:
            return generate_error('ERROR: An error has occurred with the database!', 403)
    return aiohttp.web.Response(text='OK', status=200)
