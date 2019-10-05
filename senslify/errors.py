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

import aiohttp, os, traceback, sys


class DBError(Exception):
    pass


def generate_error(text, status):
    """Generates generic errors for clients.

    Arguments:
        text (str): Informative flavor text.
        status (int): The HTTP response code.

    Returns:
        (aiohttp.web.Response): An aiohttp.web.Response object.
    """
    resp = "HTTP Error {c}: \n\n{t}".format(t=text, c=status)
    return aiohttp.web.Response(text=resp, status=status)


def traceback_str(exception):
    """Generates a formatted traceback string for developer output.

    Arguments:
        exception (Exception): The exception that triggered the traceback.

    Returns:
        (str): A formatted traceback string.
    """
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    text = 'HTTP RESPONSE 403:\n\nError: {}\nType: {}\nFile: {}\nLine Number: {}\n\nTraceback:\n{}'.format(str(exception), exc_type, fname, exc_tb.tb_lineno,
        ''.join(traceback.format_tb(exc_tb)))
    return text
