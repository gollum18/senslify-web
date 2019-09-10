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

# TODO: Refactor the errors handlers so that they catch generic errors

import aiohttp, aiohttp_jinja2
import simplejson

from datetime import datetime

from senslify.errors import traceback_str
from senslify.filters import filter_reading
from senslify.sockets import message
from senslify.verify import verify_reading


@aiohttp_jinja2.template('sensors/info.jinja2')
async def info_handler(request):
    """Defines a POST endpoint for the sensor info page.
    
    Keyword arguments:
    request -- A aiohttp.web.Request object.
    """
    # redirect to the sensors page if no sensor was provided
    if 'sensorid' not in request.query or 'groupid' not in request.query:
        location = request.app.router['sensors'].url_for()
        raise aiohttp.web.HTTPFound(location=location)
    status = 200
    
    # build the WebSocket address for the webpage
    prefix = 'wss://' if request.secure else 'ws://'
    sensorid = int(request.query['sensorid'])
    groupid = int(request.query['groupid'])
    rtypeid = int(request.app['config'].default_rtypeid)
    host = request.host
    route = '/ws'
    ws_url = prefix + host + route
    
    # build the sensor readings query
    rtypes = []
    num_readings = int(request.app['config'].num_readings)
    try:
        async for rtype in request.app['db'].get_rtypes():
            rtypes.append(rtype)
    except Exception as e:
        status = 403
        if request.app['config'].debug:
            text = 'HTTP RESPONSE 403:\n\n{}'.format(traceback_str(e))
        else:
            text = 'HTTP RESPONSE 403:\n\nAn error has occurred with the database!'
    
    # get the time span
    end = datetime.timestamp(datetime.now())
    start = datetime.timestamp(datetime.today().replace(day=1))
    # build the stats dictionary with default entries
    stats = None
    try:
        stats = await request.app['db'].stats_sensor(sensorid, groupid, 
            rtypeid, start, end)
        # replace the elements in the doc with what the webpage expects
        stats['min'] = stats['min'][0]['min']
        stats['max'] = stats['max'][0]['max']
        stats['avg'] = stats['avg'][0]['avg']
    except Exception as e:
        if request.app['config'].debug:
            text = traceback_str(e)
        else:
            text = 'HTTP RESPONSE 403:\n\nAn error has occurred with the database!'
    if status != 200:
        return aiohttp.web.Response(status=status, text=text)
    else:
        # build the response thru jinja2
        return {
            'title': 'Sensor Info',
            'sensorid': sensorid,
            'groupid': groupid,
            'rtypeid': rtypeid,
            'rtypes': rtypes,
            'stats': stats,
            'num_readings': num_readings,
            'ws_url': ws_url
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
        location = request.app.router['index'].url_for()
        raise aiohttp.web.HTTPFound(location=location)
    # construct the response and return it
    group = int(request.query['groupid'])
    status = 200
    sensors = []
    try:
        async for sensor in request.app['db'].get_sensors(group):
            sensor['url'] = build_info_url(request, sensor)
            sensors.append(sensor)
    except Exception as e:
        if request.app['config'].debug:
            text = traceback_str(e)
        else:
            text = 'HTTP RESPONSE 403:\n\nAn error has occurred with the database!'
    if status != 200:
        return aiohttp.web.Response(text=text, status=status)
    else:
        return {
            'title': 'Sensors', 
            'sensors': sensors
        }


async def upload_handler(request):
    """Defines a POST endpoint for uploading sensor data.
    
    Keyword arguments:
    request -- A aiohttp.web.Request object.
    """
    status = 200
    text = 'Request processed successfully!'
    doc = simplejson.loads(request.query['msg'])
    # TODO: Perform verification on the data passed to the handler
    if doc['sensorid'] is None:
        status = 400
        text = 'You must supply a sensor ID in your message.'
    if status == 200:
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
            status = 403
            if request.app['config'].debug:
                text = traceback_str(e)
            else:
                text = 'HTTP RESPONSE 403:\n\nAn error has occurred with the database!'
    return aiohttp.web.Response(text=text, status=status)
