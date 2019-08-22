# Name: rest.py
# Since: Aug. 22nd, 2019
# Author: Christen Ford
# Purpose: Exposes the database connector as a REST API. The primary purpose
#   of this module is to allow ad-hoc interaction with the database connector.

import aiohttp

async def rest_handler(request):
    '''
    Defines a GET handler for the '/rest' endpoint.

    Users make requests of this handler with a query string containing the
    following arguments:
        cmd: The command c to execute | c E {find, find_one}
        target: The target t to run the command against | t E {groups, rtypes, sensors, readings}.
        params: A list of key-value parameters corresponding to the targets attributes.

    This handler will return an error if the querystring is in an incorrect format.
    '''
    pass
