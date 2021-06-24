# THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
# APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
# HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT
# WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
# PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE
# DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR
# CORRECTION.

# Name: sockets.py
# Since: ~Jul. 20th, 2019
# Author: Christen Ford
# Description: Defines a handler for the info page WebSocket as well as various
#   helper functions.

import aiohttp
import simplejson

from senslify.errors import DBError
from senslify.filters import filter_reading


#
# Define WebSocket command methods
#

def _does_room_exist(rooms, groupid, sensorid):
    """ Determines if there is a room for a given sensor or not.

    Args:
        rooms (dict): A dictionary containing sensor rooms.
        groupid (int): The groupid corresponding to the room to check.
        sensorid (int): The sensorid corresponding to the room to check.
    """
    if not (groupid, sensorid) in rooms:
        return False
    return True


def _does_ws_exist(rooms, groupid, sensorid, ws):
    """Determines if a WebSocket exists in the given room or not.

    Args:
        rooms (dict): A dictionary containing sensor rooms.
        groupid (int): The groupid corresponding to the room to check attendance for.
        sensorid (int): The sensorid corresponding to the room to check attendance for.
        ws (aiohttp.web.WebSocketResponse): The WebSocket to check for.
    """
    if not _does_room_exist(rooms, groupid, sensorid):
        return False
    if ws not in rooms[(groupid, sensorid)]:
        return False
    return True


async def _leave(rooms, groupid, sensorid, ws):
    """Allows a WebSocket to leave a room

    Args:
        rooms (dict): A dictionary contaiing sensor rooms.
        groupid (int): The groupid corresponding to the room to leave.
        sensorid (int): The sensorid corresponding to the room to leave.
        ws (aiohttp.web.WebSocketResponse): The WebSocket requesting to leave the room.
    """
    # only delete the ws from the room if room exists and the ws is in the room
    if not _does_ws_exist(rooms, groupid, sensorid, ws):
        return
    del rooms[(groupid, sensorid)][ws]


async def _join(rooms, groupid, sensorid, ws):
    """Allows a WebSocket to join a room.

    Args:
        rooms (dict): A dictionary containing sensor rooms.
        groupid (int): The groupid corresponding to the room to join.
        sensorid (int): The sensorid corresponding to the room to join.
        ws (aiohttp.web.WebSocketResponse): The WebSocket to add to the room.
    """
    try:
        # create the room if it does not exist
        if sensorid not in rooms:
            rooms[(groupid, sensorid)] = dict()
        # add the client to the room if its not already there, default to temp
        if ws not in rooms[(groupid, sensorid)]:
            rooms[(groupid, sensorid)][ws] = 0
        return True
    except Exception:
        return False


async def _change_stream(rooms, groupid, sensorid, ws, rtypeid):
    """Changes the data stream the WebSocket receives.

    Args:
        rooms (dict): A dictionary containing sensor rooms.
        groupid (int): The groupid corresponding to the room the WebSocket is in.
        sensorid (int): The sensorid corresponding to the room the WebSocket is in.
        ws (aiohttp.web.WebSocketResponse): The WebSocket to change stream for.
        rtypeid (int): The stream type to change to.
    """
    # check if the ws exists, return if so
    if not _does_ws_exist(rooms, groupid, sensorid, ws):
        return
    rooms[(groupid, sensorid)][ws] = int(rtypeid)


async def message(rooms, groupid, sensorid, msg):
    """Sends a message to the participants of a room.

    Args:
        rooms (dict): A dictionary containing the sensor rooms.
        groupid: The groupid corresponding to the room to message.
        sensorid (int): The sensorid corresponding to the room to message.
        msg (dict): The message to send to all room participants (usually a reading).
    """
    # only send the message if the room exists
    if not _does_room_exist(rooms, groupid, sensorid):
        return
    # add additional fields to the message
    # create the response object for the websocket
    resp = dict()
    resp['cmd'] = 'RESP_READING'
    resp['readings'] = [{
        'rtypeid': msg['rtypeid'],
        'ts': msg['ts'],
        'val': msg['val'],
        'rstring': msg['rstring']
    }]
    try:
        # get the rtype, so we only send to clients that ask for it specifically
        rtypeid = msg['rtypeid']
    except KeyError:
        print("ERROR: KeyError has occurred sending message, 'rtypeid' not found!")
        return
    # steps through all clients in the room
    for ws, rtype in rooms[(group, sensorid)].items():
        if rtype == rtypeid:
            await ws.send_str(simplejson.dumps(resp))


# Defines the handler for the info page WebSocket
async def ws_handler(request):
    """Handles request for the servers websocket address.

    Args:
        request (aiohttp.web.Request): The request that initiated the WebSocket connection.
    """
    sensorid = 0

    ws = None
    try:
        ws = aiohttp.web.WebSocketResponse(autoclose=False)
        await ws.prepare(request)
    except aiohttp.web.WSServerHandshakeError:
        raise aiohttp.web.HTTPFound(request.app.router['index'].url_for())

    # TODO: There needs to be guards in the casting here
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            # decode the received message
            #   every value in js will be a string, cast as necessary
            js = None
            resp = dict()
            resp['cmd'] = ''
            try:
                js = simplejson.loads(msg.data)
            except simplejson.JSONDecodeError:
                resp['cmd'] = 'RESP_ERROR'
                resp['error'] = 'ERROR: Request is not a properly formed JSON message!'
            if resp['cmd'] == 'RESP_ERROR':
                await ws.send_str(simplejson.dumps(resp))
                continue
            
            if not js:
                resp['cmd'] = 'RESP_ERROR'
                resp['error'] = 'ERROR: No request was found!'
            if resp['cmd'] == 'RESP_ERROR':
                await ws.send_str(simplejson.dumps(resp))
                continue
            
            # make sure the cmd, groupid and sensorid fields are present, they are
            #   required for command execution
            if 'cmd' not in js or 'groupid' not in js or 'sensorid' not in js:
                resp['cmd'] = 'RESP_ERROR'
                resp['error'] = 'ERROR: Request requires the \'cmd\', \'groupid\' and \'sensorid\' fields!'
            if resp['cmd'] == 'RESP_ERROR':
                await ws.send_str(simplejson.dumps(resp))
                continue
            cmd = js['cmd']
            try:
                groupid = int(js['groupid'])
                sensorid = int(js['sensorid'])
            except Exception:
                resp['cmd'] = 'RESP_ERROR'
                resp['error'] = 'ERROR: \'groupid\' and \'sensorid\' must be integer numeric types.'
            if resp['cmd'] == 'RESP_ERROR':
                await ws.send_str(simplejson.dumps(resp))
                continue

            # adds the requesting websocket as a receiver for messages from
            #   the indicated sensor
            if cmd == 'RQST_JOIN':
                result = await _join(request.app['rooms'], groupid, sensorid, ws)
                resp['cmd'] = 'RESP_JOIN'
                resp['join_status'] = result
                await ws.send_str(simplejson.dumps(resp))
            # close the connection if the client requested it
            elif cmd == 'RQST_CLOSE':
                await _leave(request.app['rooms'], groupid, sensorid, ws)
                await ws.close()
                break
            # handle requests from users to switch to a different reading type
            elif cmd == 'RQST_STREAM':
                # perform verification checks
                if 'rtypeid' not in js:
                    resp['cmd'] = 'RESP_ERROR'
                    resp['error'] = 'ERROR: Request requires the \'rtypeid\' field.'
                if resp['cmd'] == 'RESP_ERROR':
                    await ws.send_str(simplejson.dumps(resp))
                    continue
                # get request info
                try:
                    rtypeid = int(js['rtypeid'])
                except Exception:
                    resp['cmd'] = 'RESP_ERROR'
                    resp['error'] = 'ERROR: \'rtypeid\' must be an integer numeric type.'
                if resp['cmd'] == 'RESP_ERROR':
                    await ws.send_str(simplejson.dumps(resp))
                    continue
                # change the stream
                await _change_stream(request.app['rooms'], groupid, sensorid, ws, rtypeid)
                # construct a response containing the top 100 readings for the stream
                resp['cmd'] = 'RESP_STREAM'
                readings = []
                try:
                    async for reading in request.app['db'].get_readings(sensorid, groupid, rtypeid):
                        reading['rstring'] = filter_reading(reading)
                        readings.append(reading)
                except DBError:
                    resp['cmd'] = 'RESP_ERROR'
                    resp['error'] = 'ERROR: There was an issue retrieving the top 100 readings for the new reading type from the database!'
                if resp['cmd'] == 'RESP_ERROR':
                    await ws.send_str(simplejson.dumps(resp))
                    continue
                resp['readings'] = readings
                # send the response to the client
                await ws.send_str(simplejson.dumps(resp))
            # handle requests for getting stats on sensors
            elif cmd == 'RQST_SENSOR_STATS':
                resp['cmd'] = 'RESP_SENSOR_STATS'
                # perform verification checks
                if ('rtypeid' not in js or
                        'start_date' not in js or
                        'end_date' not in js):
                    resp['cmd'] = 'RESP_STATS_ERROR'
                    resp['error'] = 'ERROR: Request requires the \'rtypeid\', \'start_date\', and \'end_date\' fields.'
                if resp['cmd'] == 'RESP_STATS_ERROR':
                    await ws.send_str(simplejson.dumps(resp))
                    continue
                # get request info
                try:
                    rtypeid = int(js['rtypeid'])
                    start_date = int(js['start_date'])
                    end_date = int(js['end_date'])
                except Exception:
                    resp['cmd'] = 'RESP_STATS_ERROR'
                    resp['error'] = 'ERROR: \'rtypeid\', \'start_date\', and \'end_date\' must be integer numeric types!'
                if resp['cmd'] == 'RESP_STATS_ERROR':
                    await ws.send_str(simplejson.dumps(resp))
                    continue
                # get stats info from the database
                try:
                    resp['stats'] = await request.app['db'].stats_sensor(sensorid,
                        groupid, rtypeid, start_date, end_date)
                except DBError:
                    resp['cmd'] = 'RESP_STATS_ERROR'
                    resp['error'] = 'ERROR: Cannot retrieve reading statistics, there was an issue with the database!'
                # send the response to the client
                await ws.send_str(simplejson.dumps(resp))
            elif cmd == 'RQST_DOWNLOAD':
                resp['cmd'] = 'RESP_DOWNLOAD'
                # perform verification checks
                if ('start_date' not in js or 
                        'end_date' not in js):
                    resp['cmd'] = 'RESP_DOWNLOAD_ERROR'
                    resp['error'] = 'ERROR: Request requires the \'start_date\' and \'end_date\' fields!'
                if resp['cmd'] == 'RESP_DOWNLOAD_ERROR':
                    await ws.send_str(simplejson.dumps(resp))
                    continue
                # get request info
                try:
                    groupid = int(js['groupid'])
                    start_date = int(js['start_date'])
                    end_date = int(js['end_date'])
                except Exception:
                    resp['cmd'] = 'RESP_DOWNLOAD_ERROR'
                    resp['error'] = 'ERROR: \'groupid\', \'start_date\', and \'end_date\' must be integer numeric types!'
                if resp['cmd'] == 'RESP_DOWNLOAD_ERROR':
                    await ws.send_str(simplejson.dumps(resp))
                    continue
                try:
                    resp['data'] = await request.app['db'].get_readings_by_period(sensorid,
                        groupid, start_date, end_date)
                except Exception:
                    resp['cmd'] = 'RESP_DOWNLOAD_ERROR'
                    resp['error'] = 'ERROR: Cannot retrieve readings for download, there was an issue with the database!'
                await ws.send_str(simplejson.dumps(resp))
        elif msg.type == aiohttp.WSMsgType.ERROR:
            resp = dict()
            resp['cmd'] == 'RESP_WS_ERROR'
            resp['error'] = 'WebSocket encountered an error: %s\nPlease refresh the page.'.format(ws.exception())
            ws.send_str(simplejson.dumps(resp))

    await _leave(request.app['rooms'], groupid, sensorid, ws)

    return ws


async def socket_shutdown_handler(app):
    """Defines a handler for shutting down any connected WebSockets when the
    server goes down.

    Args:
        app (aiohttp.web.Application): The web application hosting the sensor rooms.
    """
    # close any open websockets
    for groupid, sensor in app['rooms'].keys():
        for ws in app['rooms'][(groupid, sensor)].keys():
            if not ws.closed:
                # close the WebSocket
                await ws.close(code=aiohttp.WSCloseCode.GOING_AWAY,
                       message='Server shutdown')
