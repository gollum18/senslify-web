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


def verify_rest_request(request):
    """Determines if a rest request is valid.

    Arguments:
        request (aiohttp.web.Request): The REST request to validate.

    Returns:
        A tuple containing (boolean, str) indicating the whether the REST request is valid as well as a status string.
    """
    # verify that all components are necessary
    if 'cmd' not in request.query or request.query['cmd'] is None:
        return False
    if 'target' not in request.query or request.query['target'] is None:
        return False

    target = request.query['target']
    if target == 'sensors' or target == 'readings':
        if 'params' not in request.query or request.query['params'] is None:
            return False

    # get the cmd and target
    cmd = request.query['cmd']
    target = request.query['target']

    # check that the cmd is valid
    global valid_rest_cmds
    if cmd not in valid_rest_cmds:
        return False, '\'{}\' is not a valid cmd!'.format(cmd)

    # check that the target is valid
    global valid_rest_targets
    if target not in valid_rest_targets:
        return False, '\'{}\' is not a valid target!'.format(target)

    # stats can be called on groups or sensors with finer granularity
    if cmd == 'stats' and target != 'groups' and target != 'sensors':
        return False, '\'stats\' cmd can only be called on the \'readings\' target!'

    # no need to check the parameters if the target is not sensors or readings
    if target != 'sensors' and target != 'readings':
        return True, ''

    # check that the rest parameters are ok
    if not verify_rest_params(request.query['target'],
                              simplejson.loads(request.query['params'])):
        return False, 'Invalid \'params\' for target {}!'.format(target)

    # done checking
    return True, ''


def verify_rest_params(target, params):
    """Verifies the parameters of a REST request.

    Args:
        target (str): The target of the REST request.
        params (dict): A dictionary containing params corresponding to the target.

    Returns:
        (boolean): Whether the REST params are valid.
    """
    # groupid is required regardless
    if 'groupid' not in params:
        return False

    # additionally, sensorid is required for sensors
    if target == 'sensors':
        if 'sensorid' not in params:
            return False

    return True


def verify_reading(reading):
    """Determines if a reading is in the correct format.
    This method does not verify that keys are correct.

    Args:
        reading (dict): The reading to verify.

    Returns:
        True if the reading is valid, False otherwise.
    """
    # make sure the reading type is a dictionary
    if type(reading) is not dict:
        return False

    # check that all the required fields are present
    if 'sensorid' not in reading:
        return False
    if 'groupid' not in reading:
        return False
    if 'rtypeid' not in reading:
        return False
    if 'ts' not in reading:
        return False
    if 'val' not in reading:
        return False

    # TODO: Check the individual data fields as well

    return True
