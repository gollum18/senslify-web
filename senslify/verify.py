# THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
# APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
# HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT
# WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
# PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE
# DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR
# CORRECTION.

# Name: verify.py
# Since: Aug. 8th, 2019
# Author: Christen Ford
# Description: Contains useful methods for verifying Senslify data objects.

import simplejson


# used in the rest validation command
valid_rest_cmds = ('find', 'stats')
valid_rest_targets = ('groups', 'rtypes', 'sensors', 'readings')


async def _verify_find_request(request, params):
    """Verifies a received \'find\' REST command.

    Args:
        request (aiohttp.Web.Request): The request from the client.
        params (dict-like): A dictionary like object containing the REST command request parameters.

    Returns:
        (boolean, str): A boolean indicating if the request is valid. The other parameter is an error
        message if the boolean is True, and is None otherwise.
    """
    if 'target' not in params: return False, 'ERROR: Request params requires \'target\' field!'
    target = params['target']
    if target != 'groups' and target != 'rtypes' and target != 'sensors' and target != 'readings':
        return False, 'ERROR: Request parameter \'target\' must be one of \{\'groups\', \'rtypes\', \'sensors\', \'readings\'\}!'
    if target == 'sensors':
        if 'groupid' not in params: return False, 'ERROR: Request params requires \'groupid\' field!'
        try:
            groupid = int(params['groupid'])
        except Exception:
            return False, 'ERROR: A parameter is of incorrect type!'
        if groupid < 0: return False, 'ERROR: Request parameter \'groupid\' must be >= 0!'
        if not await request.app['db'].does_group_exist(groupid):
            return False, 'ERROR: No such group provisioned into the system!'
    elif target == 'readings':
        if 'groupid' not in params: return False, 'ERROR: Request params requires \'groupid\' field!'
        if 'sensorid' not in params: return False, 'ERROR: Request params requires \'sensorid\' field!'
        try:
            groupid = int(params['groupid'])
            sensorid = int(params['sensorid'])
        except Exception:
            return False, 'ERROR: A parameter is on incorrect type!'
        if groupid < 0: return False, 'ERROR: Request parameter \'groupid\' must be >= 0!'
        if sensorid < 0: return False, 'ERROR: Request parameter \'sensorid\' must be >= 0!'
        if not await request.app['db'].does_group_exist(groupid):
            return False, 'ERROR: No such group provisioned into the system!'
        if not await request.app['db'].does_sensor_exist(sensorid, groupid):
            return False, 'ERROR: No such sensor provisioned into the system!'
    return True, None


async def _verify_stats_request(request, params):
    """Verifies a received RQST_STATS WebSocket command.

    Args:
        request (aiohttp.Web.Request): The request from the client.
        json (dict-like): A dictionary like object containing the WebSocket command request parameters.

    Returns:
        (boolean, str): A boolean indicating if the request is valid. The other parameter is an error
        message if the boolean is True, and is None otherwise.
    """
    if 'target' not in params: return False, 'ERROR: Request params requires \'target\' field!'
    if 'groupid' not in params: return False, 'ERROR: Request params requires \'groupid\' field!'
    if 'rtypeid' not in params: return False, 'ERROR: Request params requires \'rtypeid\' field!'
    if 'start_ts' not in params: return False, 'ERROR: Request params requires \'start_ts\' field!'
    if 'end_ts' not in params: return False, 'ERROR: Request params requires \'end_ts\' field!'
    target = params['target']
    if target != 'groups' and target != 'sensors': 
        return False, 'ERROR: Request parameter \'target\' must be one of \{\'groups\', \'sensors\'\}'
    if target == 'sensors':
        if 'sensorid' not in params: return False, 'ERROR: Request params requires \'sensorid\' field!'
    try:
        groupid = int(params['groupid'])
        rtypeid = int(params['rtypeid'])
        start_ts = int(params['start_ts'])
        end_ts = int(params['end_ts'])
        if target == 'sensors': 
            sensorid = int(params['sensorid'])
            if sensorid < 0: return False, 'ERROR: Request parameter \'sensorid\' must be >= 0!'
    except Exception:
        return False, 'ERROR: A parameter is of incorrect type!'
    if groupid < 0: return False, 'ERROR: Request parameter \'groupid\' must be >= 0!'
    if rtypeid < 0: return False, 'ERROR: Request parameter \'rtypeid\' must be >= 0!'
    if start_ts < 0: return False, 'ERROR: Request parameter \'start_ts\' must be >= 0!'
    if end_ts < 0: return False, 'ERROR: Request parameter \'end_ts\' must be >= 0!'
    if not await request.app['db'].does_group_exist(groupid):
        return False, 'ERROR: No such group provisioned into the system!'
    if not await request.app['db'].does_rtype_exist(rtypeid):
        return False, 'ERROR: No such reading type provisioned into the system!'
    return True, None


async def _verify_download_request(request, params):
    """Verifies a received RQST_DOWNLOAD WebSocket command or \'download\' REST command.

    Args:
        request (aiohttp.Web.Request): The request from the client.
        json (dict-like): A dictionary like object containing the WebSocket command request parameters.

    Returns:
        (boolean, str): A boolean indicating if the request is valid. The other parameter is an error
        message if the boolean is True, and is None otherwise.
    """
    if 'sensorid' not in params: return False, 'ERROR: Request params requires \'sensorid\' field!'
    if 'groupid' not in params: return False, 'ERROR: Request params requires \'groupid\' field!'
    if 'start_ts' not in params: return False, 'ERROR: Request params requires \'start_ts\' field!'
    if 'end_ts' not in params: return False, 'ERROR: Request params requires \'end_ts\' field!'
    try:
        groupid = int(params['groupid'])
        sensorid = int(params['sensorid'])
        start_ts = int(params['start_ts'])
        end_ts = int(params['end_ts'])
    except Exception:
        return False, 'ERROR: A parameter is of incorrect type!'
    if groupid < 0: return False, 'ERROR: Request parameter \'groupid\' must be >= 0.'
    if sensorid < 0: return False, 'ERROR: Request parameter \'sensorid\' must be >= 0.'
    if start_ts < 0: return False, 'ERROR: Request parameter \'start_ts\' must be >= 0.'
    if end_ts < 0: return False, 'ERROR: Request parameter \'start_ts\' must be >= 0.'
    if not await request.app['db'].does_group_exist(groupid):
        return False, 'ERROR: No such group provisioned into the system!'
    if not await request.app['db'].does_sensor_exist(sensorid, groupid):
        return False, 'ERROR: No such sensor provisioned into the system!'
    return True, None


async def _verify_upload_request(request, params):
    """Verifies a received \'upload\' REST command.

    Args:
        request (aiohttp.Web.Request): The request from the client.
        params (dict-like): A dictionary like object containing the REST command request parameters.

    Returns:
        (boolean, str): A boolean indicating if the request is valid. The other parameter is an error
        message if the boolean is True, and is None otherwise.
    """
    if 'readings' not in params: return False, 'ERROR: Request params requires \'readings\' field!'
    readings = params['readings']
    for reading in readings:
        if 'groupid' not in reading: return False, 'ERROR: Request params requires \'groupid\' field!'
        if 'sensorid' not in reading: return False, 'ERROR: Request params requires \'sensorid\' field!'
        if 'rtypeid' not in reading: return False, 'ERROR: Request params requires \'rtypeid\' field!'
        if 'val' not in reading: return False, 'ERROR: Request params requires \'val\' field!'
        if 'ts' not in reading: return False, 'ERROR: Request params requires \'ts\' field!'
        try:
            groupid = int(reading['groupid'])
            sensorid = int(reading['sensorid'])
            rtypeid = int(reading['rtypeid'])
            val = float(reading['val'])
            ts = int(reading['ts'])
        except Exception:
            return False, 'ERROR: A parameter is of incorrect type!'
        if groupid < 0: return False, 'ERROR: Request parameter \'groupid\' must be >= 0.'
        if sensorid < 0: return False, 'ERROR: Request parameter \'sensorid\' must be >= 0.'
        if rtypeid < 0: return False, 'ERROR: Request parameter \'rtypeid\' must be >= 0.'
        if ts < 0: return False, 'ERROR: Request parameter \'ts\' must be >= 0.'
        if not await request.app['db'].does_group_exist(groupid):
            return False, 'ERROR: No such group provisioned into the system!'
        if not await request.app['db'].does_sensor_exist(sensorid, groupid):
            return False, 'ERROR: No such sensor provisioned into the system!'
        if not await request.app['db'].does_rtype_exist(rtypeid):
            return False, 'ERROR: No such reading type provisioned into the system!'
    return True, None


async def _verify_provision_request(request, params):
    """Verifies a received \'provision\' REST command.

    Args:
        request (aiohttp.Web.Request): The request from the client.
        params (dict-like): A dictionary like object containing the REST command request parameters.

    Returns:
        (boolean, str): A boolean indicating if the request is valid. The other parameter is an error
        message if the boolean is True, and is None otherwise.
    """
    if 'target' not in params: return False, 'ERROR: Request params requires \'target\' field!'
    target = params['target']
    if target != 'sensor' or target != 'group':
        return False, 'ERROR: Invalid \'target\' specified! Must be one of \{\'sensor\', \'group\'\}.'
    if target == 'group':
        if 'groupid' not in params: return False, 'ERROR: Request params requires \'groupid\' field!'
        try:
            groupid = int(params['groupid'])
        except Exception:
            return False, 'ERROR: Request parameter \'groupid\' must be an integer!'
        if groupid < 0: return False, 'ERROR: Request parameter \'groupid\' must be >= 0!'
        if await request.app['db'].does_group_exist(groupid):
            return False, 'ERROR: Group is already provisioned into the system.'
    elif target == 'sensor':
        if 'sensorid' not in params: return False, 'ERROR: Request params requires \'sensorid\' field'
        try:
            sensorid = int(params['sensorid'])
        except Exception:
            return False, 'ERROR: Request parameter \'sensorid\' must be an integer!'
        if sensorid < 0: return False, 'ERROR" Request parameter \'sensorid\' must be >= 0!'
    if 'alias' in params:
        if not params['alias']: return False, 'ERROR: Request parameter \'alias\' must contain at least one (1) character!'
    return True, None


async def _verify_join_command(request, params):
    """Verifies a received RQST_JOIN WebSocket command.

    Args:
        request (aiohttp.Web.Request): The request from the client.
        json (dict-like): A dictionary like object containing the WebSocket command request parameters.

    Returns:
        (boolean, str): A boolean indicating if the request is valid. The other parameter is an error
        message if the boolean is True, and is None otherwise.
    """
    if 'groupid' not in params: return False, 'ERROR: Request requires \'groupid\' field!'
    if 'sensorid' not in params: return False, 'ERROR: Request requires \'sensorid\' field!'
    try:
        groupid = int(params['groupid'])
        sensorid = int(params['sensorid'])
    except Exception:
        return False, 'ERROR: A parameter is of incorrect type!'
    if groupid < 0: return False, 'ERROR: Request parameter \'groupid\' must be >= 0.'
    if sensorid < 0: return False, 'ERROR: Request parameter \'sensorid\' must be >= 0.'
    if not await request.app['db'].does_group_exist(groupid):
        return False, 'ERROR: No such group provisioned into the system!'
    if not await request.app['db'].does_sensor_exist(sensorid, groupid):
        return False, 'ERROR: No such sensor provisioned into the system!'
    return True, None


async def _verify_close_command(request, params):
    """Verifies a received RQST_CLOSE WebSocket command.

    Args:
        request (aiohttp.Web.Request): The request from the client.
        json (dict-like): A dictionary like object containing the WebSocket command request parameters.

    Returns:
        (boolean, str): A boolean indicating if the request is valid. The other parameter is an error
        message if the boolean is True, and is None otherwise.
    """
    if 'groupid' not in params: return False, 'ERROR: Request requires \'groupid\' field!'
    if 'sensorid' not in params: return False, 'ERROR: Request requires \'sensorid\' field!'
    try:
        groupid = int(params['groupid'])
        sensorid = int(params['sensorid'])
    except Exception:
        return False, 'ERROR: A parameter is of incorrect type!'
    if groupid < 0: return False, 'ERROR: Request parameter \'groupid\' must be >= 0.'
    if sensorid < 0: return False, 'ERROR: Request parameter \'sensorid\' must be >= 0.'
    if not await request.app['db'].does_group_exist(groupid):
        return False, 'ERROR: No such group provisioned into the system!'
    if not await request.app['db'].does_sensor_exist(sensorid, groupid):
        return False, 'ERROR: No such sensor provisioned into the system!'
    return True, None


async def _verify_stream_command(request, params):
    """Verifies a received RQST_STREAM WebSocket command.

    Args:
        request (aiohttp.Web.Request): The request from the client.
        json (dict-like): A dictionary like object containing the WebSocket command request parameters.

    Returns:
        (boolean, str): A boolean indicating if the request is valid. The other parameter is an error
        message if the boolean is True, and is None otherwise.
    """
    if 'rtypeid' not in params: return False, 'ERROR: Request requires \'rtypeid\' field!'
    try:
        rtypeid = int(params['rtypeid'])
    except Exception:
        return False, 'ERROR: A parameter is of incorrect type!'
    if rtypeid < 0: return False, 'ERROR: Request parameter \'rtypeid\' must be >= 0'
    if not await request.app['db'].does_rtype_exist(rtypeid):
        return False, 'ERROR: No such reading type provisioned into the system!'
    return True, None


async def verify_ws_request(request, json):
    """Verifies a received WebSocket request. This function routes requests to other verification
    functions based on the \'cmd\' fielkd specified in the json message accompanying the request.

    Args:
        request (aiohttp.Web.Request): The request from the client.
        json (dict-like): A dictionary like object containing the WebSocket command request parameters.

    Returns:
        (boolean, str): A boolean indicating if the request is valid. The other parameter is an error
        message if the boolean is True, and is None otherwise.
    """
    if 'cmd' not in json: return False, 'ERROR: Request requires \'cmd\' field!'
    cmd = json['cmd']
    if cmd == 'RQST_JOIN':
        return await _verify_join_command(request, json)
    elif cmd == 'RQST_CLOSE':
        return await _verify_close_command(request, json)
    elif cmd == 'RQST_STREAM':
        return await _verify_stream_command(request, json)
    elif cmd == 'RQST_SENSOR_STATS':
        return await _verify_stats_request(request, json)
    elif cmd == 'RQST_DOWNLOAD':
        return await _verify_download_request(request, json)
    else: return False, 'ERROR: \'cmd\' must be one of \{\'RQST_JOIN\', \'RQST_CLOSE\', \'RQST_STREAM\', \'RQST_SENSOR_STATS\', \'RQST_DOWNLOAD\'\}!'


async def verify_rest_request(request):
    """Determines if a rest request is valid.

    Arguments:
        request (aiohttp.web.Request): The REST request to validate.

    Returns:
        A tuple containing (boolean, str) indicating the whether the REST request is valid as well as a status string.
    """
    json = await request.json()
    # check if the command and parameters are present
    if 'cmd' not in json: return False, 'ERROR: Request requires \'cmd\' field!'
    if 'params' not in json: return False, 'ERROR: Request requires \'params\' field!'
    cmd = json['cmd']
    params = json['params']
    if cmd == 'find':
        return await _verify_find_request(request, params)
    elif cmd == 'stats':
        return await _verify_stats_request(request, params)
    elif cmd == 'download':
        return await _verify_download_request(request, params)
    elif cmd == 'upload':
        return await _verify_upload_request(request, params)
    elif cmd == 'provision':
        return await _verify_provision_request(request, params)
    else: return False, 'ERROR: \'cmd\' must be one of \{\'find\', \'stats\', \'download\', \'upload\', \'provision\'\}!'
