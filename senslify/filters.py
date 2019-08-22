# Name: filters.py
# Since: Aug 15th, 2019
# Author: Christen Ford
# Purpose: Houses filter functions for use with rendering via aiohttp_jinja2.

from babel.dates import format_datetime

def filter_datetime(value, format='medium'):
    """'i18n' compliant datetime filter for jinja2.
    Taken from: https://stackoverflow.com/questions/4830535/how-do-i-format-a-date-in-jinja2
    
    Keyword arguments:
    value -- The value to format.
    format -- The format to use, either medium or full.
    """
    if format == 'full':
        format="EEEE, d. MMMM y 'at' HH:mm:ss"
    elif format == 'medium':
        format="EE dd.MM.y HH:mm:ss"
    return format_datetime(value, format)
    

def filter_reading(reading):
    """Generates a formatted string for a reading.
    
    Keyword arguments:
    reading -- A reading from a sensor, must be a dictionary.
    """
    if type(reading) is not dict:
        return 'Unable to generate format string, reading is not a dict!'
    if 'ts' not in reading or 'val' not in reading:
        return 'Unable to generate format string, reading does not contain all necessary information!'
    dt = filter_datetime(reading['ts'])
    return 'Time: {}, Value: {}'.format(dt, reading['val'])
