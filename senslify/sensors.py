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


def build_info_url(request, sensor):
    """Helper function that creates a url for a given sensor.

    This function is called primarily by the sensors_handler function to
    generate links to the sensor info page.

    Arguments:
        (request): - The request that wants the sensor url.
        (sensor): The sensor to generate a url for.
    """
    try:
        route = request.app.router['info'].url_for().with_query(
            {
                'sensorid': sensor['sensorid'],
                'groupid': sensor['groupid'],
                'alias': sensor['alias']
            }
        )
        return route
    except Exception as e:
        if request.app.config['debug']:
            return generate_error(traceback_str(e), 403)
        else:
            return generate_error('ERROR: Internal server issue occurred!', 403)


@aiohttp_jinja2.template('sensors/info.jinja2')
async def info_handler(request):
    """Defines a GET endpoint for the sensor info page.

    Arguments:
        request (aiohttp.web.Request): An aiohttp.web.Request object.

    Returns:
        (aiohttp.web.Response): An aiohttp.web.Response object.
    """
    # redirect to the sensors page if no sensor was provided
    if 'sensorid' not in request.query or 'groupid' not in request.query:
        return generate_error('ERROR: Request must contain both \'sensorid\' and \'groupid\' fields!', 400)

    # build the WebSocket address for the webpage
    prefix = 'wss://' if request.secure else 'ws://'
    sensorid = 0
    groupid = 0
    rtypeid = 0
    try:
        sensorid = int(request.query['sensorid'])
        groupid = int(request.query['groupid'])
        alias = request.query['alias']
        rtypeid = int(request.app['config'].default_rtypeid)
        max_join_attempts = int(request.app['config'].max_join_attempts)
        max_reading_deviation = float(request.app['config'].max_reading_deviation)
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
            'title': f'Sensor Info for Sensor \'{alias}\'',
            'sensorid': sensorid,
            'groupid': groupid,
            'alias': alias,
            'rtypeid': rtypeid,
            'rtypes': rtypes,
            'num_readings': num_readings,
            'ws_url': ws_url,
            'max_join_attempts': max_join_attempts,
            'max_reading_deviation': max_reading_deviation,
            'start_date': start,
            'end_date': end
        }


@aiohttp_jinja2.template('sensors/sensors.jinja2')
async def sensors_handler(request):
    """Defines a GET endpoint for the sensors listing page.

    Arguments:
        (request): An aiohttp.web.Request object.
    """
    # redirect to the index page if no group was provided
    if 'groupid' not in request.query or 'alias' not in request.query:
        return generate_error('ERROR: Request must contain a \'groupid\' and an \'alias\' field!', 400)
    
    sensors = []
    try:
        groupid = int(request.query['groupid'])
        alias = request.query['alias']
        async for sensor in request.app['db'].get_sensors(groupid):
            url = build_info_url(request, sensor)
            # if there was an error building the info url, return the error page
            if isinstance(url, aiohttp.web.Response):
                return url
            sensor['url'] = url
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
            'title': f'Sensors for group \'{alias}\'',
            'sensors': sensors
        }
