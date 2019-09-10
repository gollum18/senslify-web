# THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
# APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
# HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT
# WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
# PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE
# DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR
# CORRECTION.

# Name: errors.py
# Since: 9/6/2019
# Author: Christen Ford
# Purpose: Defines methods for generating context-specific error Responses.

import aiohttp

def generate_rest_error(reason):
    """Generates errors for the '/rest' handler.
    
    Arguments:
        reason (str): The reason the error occurred.
    Returns:
        (aio.http.Response): A Rseponse object.
    """
    status = 400
    text = "HTTP 400 ERROR: Command not understood or invalid target/parameters sent!"
    text += "\nReason: {}".format(reason)
    return aiohttp.web.Response(status=status, text=text)