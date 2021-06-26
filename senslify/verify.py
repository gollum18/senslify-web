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


def _verify_find_request(params):
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


def _verify_stats_request(params):
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
    return True, None


def _verify_download_request(params):
    if 'sensorid' not in params: return False, 'ERROR: Request params requires \'sensorid\' field!'
    if 'groupid' not in params: return False, 'ERROR: Request params requires \'groupid\' field!'
    if 'start_ts' not in params: return False, 'ERROR: Request params requires \'start_ts\' field!'
    if 'end_ts' not in params: return False, 'ERROR: Request params requires \'end_ts\' field!'
    try:
        groupid = int(params['groupid'])
        sensorid = int(params['sensorid'])
        val = float(params['val'])
        ts = int(params['ts'])
    except Exception:
        return False, 'ERROR: A parameter is of incorrect type!'
    if groupid < 0: return False, 'ERROR: Request parameter \'groupid\' must be >= 0.'
    if sensorid < 0: return False, 'ERROR: Request parameter \'sensorid\' must be >= 0.'
    if ts < 0: return False, 'ERROR: Request parameter \'ts\' must be >= 0.'
    return True, None


def _verify_upload_request(params):
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
    return True, None


def _verify_provision_request(params):
    if 'target' not in params: return False, 'ERROR: Request params requires \'target\' field!'
    if 'groupid' not in params: return False, 'ERROR: Request params requires \'groupid\' field!'
    try:
        groupid = int(params['groupid'])
    except Exception:
        return False
    if groupid < 0: return False, 'ERROR: Request paramters \'groupid\' must be >= 0!'
    return True, None


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
        return _verify_find_request(params)
    elif cmd == 'stats':
        return _verify_stats_request(params)
    elif cmd == 'download':
        return _verify_download_request(params)
    elif cmd == 'upload':
        return _verify_upload_request(params)
    elif cmd == 'provision':
        return _verify_provision_request(params)
    else: return False, 'ERROR: \'cmd\' must be one of \{\'find\', \'stats\', \'download\', \'upload\', \'provision\'\}!'
