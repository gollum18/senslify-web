# THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
# APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
# HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT
# WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
# PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE
# DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR
# CORRECTION.

# Name: rest.py
# Since: Aug. 22nd, 2019
# Author: Christen Ford
# Purpose: Exposes the database connector as a REST API. The primary purpose
#   of this module is to allow ad-hoc interaction with the database connector.
#
# For the methods defined in this module that return data such as find and stats,
#   they will always return data in the body of the Response as a serialized
#   JSON object.

import aiohttp
import simplejson
from random_word import RandomWords

from senslify.errors import generate_error, traceback_str, DBError
from senslify.filters import filter_reading
from senslify.sockets import message
from senslify.verify import verify_rest_request


word_gen = RandomWords()
def _generate_alias(n=3):
    '''Returns an n-word plain-English alias separated by hyphens.

    Arguments:
        n (int): The number of words in the alias (default: 3).

    Returns:
        (str): A string containing hyphenated plain-English words.
    '''
    if n <= 0: n = 3
    words = [word_gen.get_random_word() for i in range(n)]
    words = [w for w in words if w]
    alias = '-'.join(words)
    return alias


async def _download_handler(request, params):
    """Defines a handler for the download target.

    Args:
        request (aiohttp.web.Request): The request that initiated the REST handler.
        params (dict): A dictionary containing parameters for the target.

    Returns:
        (aiohttp.web.Response) A Response object containing the results of
        executing the downloads_handler as a serialized JSON object in its body.
        Statistics are keyed via the 'download' key.
    """
    # validation is performed in the rest dispatching method
    try:
        sensorid = int(params['sensorid'])
        groupid = int(params['groupid'])
        start_ts = int(params['start_ts'])
        end_ts = int(params['end_ts'])
        resp_body = dict()
        # call the appropriate db handler based on target
        resp_body['readings'] = await request.db.get_readings_by_period(sensorid, groupid, start_ts, end_ts)
    except Exception as e:
        if request.app.config['debug']:
            return aiohttp.web.Response(traceback_str(e), 403)
        else:
            return aiohttp.web.Response('ERROR: Unable to understand target/parameters!', 403)
    # the standard return - if we got here, then everything went ok
    return aiohttp.web.Response(body=simplejson.dumps(resp_body))


async def _find_handler(request, params):
    """Defines a handler for the find target.

    Args:
        request (aiohttp.web.Request): The request that initiated the REST handler.
        params (dict): A dictionary containing parameters for the target.

    Returns:
        (aiohttp.web.Response): A Response object containing the results of
        executing the find_handler as a serialized JSON object in its body.
        Documents are keyed via the 'docs' key.
    """
    # define the results set
    docs = []

    try:
        target = params['target']
        # target handler for groups
        if target == 'groups':
            for doc in request.app['db'].get_groups():
                docs.append(doc)
        # target handler for rtypes
        elif target == 'rtypes':
            for doc in request.app['db'].get_rtypes():
                docs.append(doc)
        # target handler for sensors
        elif target == 'sensors':
            groupid = params['groupid']
            for doc in request.app['db'].get_sensors(groupid):
                docs.append(doc)
        elif target == 'readings':
            sensorid = params['sensorid']
            groupid = params['groupid']
            for doc in request.app['db'].get_readings(sensorid, groupid):
                docs.append(doc)
    except Exception as e:
        if request.app.config['debug']:
            return generate_error(traceback_str(e), 403)
        else:
            return generate_error('ERROR: There was an issue understanding your request!', 403)

    # build and return the response
    resp_body = []
    resp_body['docs'] = docs
    return aiohttp.web.Response(body=simplejson.dumps(resp_body))


async def _stats_handler(request, params):
    """Defines a handler for the stats target.

    Args:
        request (aiohttp.web.Request): The request that initiated the REST handler.
        params (dict): A dictionary containing parameters for the target.

    Returns:
        (aiohttp.web.Response) A Response object containing the results of
        executing the stats_handler as a serialized JSON object in its body.
        Statistics are keyed via the 'stats' key.
    """
    # validation is performed in the rest dispatching method
    target = params['target']
    groupid = int(params['groupid'])
    rtypeid = int(params['rtypeid'])
    start_ts = int(params['start_ts'])
    end_ts = int(params['end_ts'])
    resp_body = dict()
    # call the appropriate db handler based on target
    try:
        if target == 'groups':
            resp_body['stats'] = await request.db.stats_group(groupid, rtypeid, start_ts, end_ts)
        elif target == 'sensors':
            sensorid = int(params['sensorid'])
            resp_body['stats'] = await request.db.stats_sensor(sensorid, groupid, rtypeid, start_ts, end_ts)
    except Exception as e:
        if request.app.config['debug']:
            return generate_error(traceback_str(e), 403)
        else:
            return generate_error('ERROR: There was an issue understanding your request!', 403)
    # the standard return - if we got here, then everything went ok
    return aiohttp.web.Response(body=simplejson.dumps(resp_body))


async def _provision_handler(request, params):
    """Defines a GET endpoint for provisioning wireless sensors with the system.

    Arguments:
        (request): An aiohttp.web.Request object where GET parameters include at 
        least a \'groupid\'.

    Returns:
        (aiohttp.web.Response): A Response object where the body is a stringified
        JSON object containing the wireless sensors sensor identifier as well as
        the alias.
    """
    if 'groupid' not in params:
        return generate_error('ERROR: Request must contain a \'groupid\' field!', 400)
    target = params['target']

    if target == 'sensor':
        sensor_alias = None
        groupid = int(params['groupid'])
        if 'alias' in params:
            sensor_alias = params['alias']
        else:
            sensor_alias = _generate_alias()
        group_inserted = False
        try:
            max_sensorid = None
            try:
                doc = await request.app['db'].find_max_sensorid_in_group(groupid)
                max_sensorid = int(doc['max'])
            except DBError:
                max_sensorid = -1
            sensorid = max_sensorid + 1
            result, e = await request.app['db'].insert_sensor(sensorid, groupid, sensor_alias)
            if e:
                raise e
        except Exception as e:
            if request.app['config'].debug:
                return generate_error(traceback_str(e), 403)
            else:
                return generate_error('ERROR: An error has occurred with the database!', 403)
        resp_body = dict()
        resp_body['sensorid'] = sensorid
        resp_body['sensor_alias'] = sensor_alias
        if group_inserted:
            resp_body['group_alias'] = group_alias
        return aiohttp.web.Response(text=simplejson.dumps(resp_body), status=200)
    elif target == 'group':
        if 'alias' in params:
            group_alias = params['alias']
        else:
            group_alias = _generate_alias()
        try:
            max_groupid = None
            try:
                doc = await request.app['db'].find_max_groupid()
                max_groupid = int(doc['max'])
            except DBError:
                max_groupid = -1
            groupid = max_groupid + 1
            result, e = await request.app['db'].insert_group(groupid, group_alias)
            if e:
                raise e
        except Exception as e:
            if request.app['config'].debug:
                return generate_error(traceback_str(e), 403)
            else:
                return generate_error('ERROR: An error has occurred with the database!', 403)
        resp_body = dict()
        resp_body['groupid'] = groupid
        resp_body['group_alias'] = group_alias
        return aiohttp.web.Response(text=simplejson.dumps(resp_body), status=200)
    else:
        return generate_error('ERROR: Invalid \'target\' specified! Must be one of \{\'sensor\', \'group\'\}.', 400)


async def _upload_handler(request, params):
    """Defines a POST endpoint for uploading sensor data.

    Arguments:
        (request) A aiohttp.web.Request object.
    """
    try:
        readings = params['readings']
        # broadcast to listeners
        for reading in readings:
            # generate the string version of the message for output on page
            reading['rstring'] = filter_reading(reading)
            # send the message to the room
            await message(request.app['rooms'], reading['groupid'], reading['sensorid'], reading)
        # insert into database
        await request.app['db'].insert_readings(readings)
    except Exception as e:
        if request.app['config'].debug:
            return generate_error(traceback_str(e), 403)
        else:
            return generate_error('ERROR: An error has occurred with the database!', 403)
    return aiohttp.web.Response(text='OK', status=200)


async def rest_handler(request):
    """Defines a GET handler for the '/rest' endpoint.

    Users make requests of this handler with a query string containing the following arguments:
        cmd: The command c to execute | c E {find, stats}
        params: A list of key-value parameters corresponding to the commands attributes.

    This handler will return an error if the querystring is in an incorrect format.

    Args:
        request (aiohttp.web.Request): The web request that initiated the handler.
    """
    # verify the request
    valid, reason = await verify_rest_request(request)
    if not valid:
        return generate_error(reason, 400)
    json = await request.json()
    # get the parameters
    cmd = json['cmd']
    params = json['params']
    # pass off to the correct target handler
    if cmd == 'find':
        response = await _find_handler(request, params)
    elif cmd == 'stats':
        response = await _stats_handler(request, params)
    elif cmd == 'download':
        response = await _download_handler(request, params)
    elif cmd == 'upload':
        response = await _upload_handler(request, params)
    elif cmd == 'provision':
        response = await _provision_handler(request, params)
    # return the response we get back fgrom the handler
    return response