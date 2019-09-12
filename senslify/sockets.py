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

from senslify.filters import filter_reading

# Define WebSocket command methods

def _does_room_exist(rooms, sensorid):
    """ Determines if there is a room for a given sensor or not.
    
    Args:
        rooms (dict): A dictionary containing sensor rooms.
        sensorid (int): The sensorid corresponding to the room to check for.
    """
    if not sensorid in rooms:
        return False
    return True


def _does_ws_exist(rooms, sensorid, ws):
    """Determines if a WebSocket exists in the given room or not.
    
    Args:
        rooms (dict): A dictionary containing sensor rooms.
        sensorid (int): The sensorid corresponding to the room to check attendance for.
        ws (aiohttp.web.WebSocketResponse): The WebSocket to check for.
    """
    if not _does_room_exist(rooms, sensorid):
        return False
    if ws not in rooms[sensorid]:
        return False
    return True    


async def _leave(rooms, sensorid, ws):
    """Allows a WebSocket to leave a room
    
    Args:
        rooms (dict): A dictionary contaiing sensor rooms.
        sensorid (int): The sensorid corresponding to the room to leave.
        ws (aiohttp.web.WebSocketResponse): The WebSocket requesting to leave the room.
    """
    # only delete the ws from the room if room exists and the ws is in the room
    if not _does_ws_exist(rooms, sensorid, ws):
        return
    del rooms[sensorid][ws]


async def _join(rooms, sensorid, ws):
    """Allows a WebSocket to join a room.
    
    Args:
        rooms (dict): A dictionary containing sensor rooms.
        sensorid (int): The sensorid corresponding to the room to join.
        ws (aiohttp.web.WebSocketResponse): The WebSocket to add to the room.
    """
    # create the room if it does not exist
    if sensorid not in rooms:
        rooms[sensorid] = dict()
    # add the client to the room if its not already there, default to temp
    if ws not in rooms[sensorid]:
        rooms[sensorid][ws] = 0


async def _change_stream(rooms, sensorid, ws, rtype):
    """Changes the data stream the WebSocket receives.
    
    Args:
        rooms (dict): A dictionary containing sensor rooms.
        sensorid (int): The sensorid corresponding to the room the WebSocket is in.
        ws (aiohttp.web.WebSocketResponse): The WebSocket to change stream for.
        rtype (int): The stream type to change to.
    """
    # check if the ws exists, return if so
    if not _does_ws_exist(rooms, sensorid, ws):
        return
    rooms[sensorid][ws] = int(rtype)
    
    
async def message(rooms, sensorid, msg):
    """Sends a message to the participants of a room.
    
    Args:
        rooms (dict): A dictionary containing the sensor rooms.
        sensorid (int): The sensorid corresponding to the room to message.
        msg (dict): The message to send to all room participants (usually a reading).
    """
    # only send the message if the room exists
    if not _does_room_exist(rooms, sensorid):
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
    # get the rtype, so we only send to clients that ask for it specifically
    rtypeid = msg['rtypeid']
    # steps through all clients in the room
    for ws, rtype in rooms[sensorid].items():
        if rtype == rtypeid:
            await ws.send_str(simplejson.dumps(resp))


# Defines the handler for the info page WebSocket
async def ws_handler(request):
    """Handles request for the servers websocket address.
    
    Args:
        request (aiohttp.web.Request): The request that initiated the WebSocket connection.
    """
    sensorid = 0
    
    ws = aiohttp.web.WebSocketResponse(autoclose=False, heartbeat=3)
    await ws.prepare(request)

    # TODO: There needs to be guards in the casting here
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            # decode the received message
            #   every value in js will be a string, cast as necessary
            js = simplejson.loads(msg.data)
            # make sure the cmd and sensorid fields are present, they are 
            #   required for command execution
            if 'cmd' not in js or 'sensorid' not in js:
                continue
            cmd = js['cmd'];
            sensorid = int(js['sensorid'])
            
            # adds the requesting websocket as a receiver for messages from
            #   the indicated sensor
            if cmd == 'RQST_JOIN':
                await _join(request.app['rooms'], sensorid, ws)
            # close the connection if the client requested it
            elif cmd == 'RQST_CLOSE':
                await _leave(request.app['rooms'], sensorid, ws)
                await ws.close()
                break
            # handle requests from users to switch to a different reading type
            elif cmd == 'RQST_STREAM':
                # perform verification checks
                if 'groupid' not in js or 'rtypeid' not in js:
                    continue
                # get request info
                groupid = int(js['groupid'])
                rtypeid = int(js['rtypeid'])
                # change the stream
                await _change_stream(request.app['rooms'], sensorid, ws, rtypeid)
                # construct a response containing the top 100 readings for the stream
                resp = dict()
                resp['cmd'] = 'RESP_STREAM'
                readings = []
                async for reading in request.app['db'].get_readings(sensorid, groupid, rtypeid):
                    reading['rstring'] = filter_reading(reading)
                    readings.append(reading)
                resp['readings'] = readings
                # send the response to the client
                await ws.send_str(simplejson.dumps(resp))
            # handle requests for getting stats on sensors
            elif cmd == 'RQST_SENSOR_STATS':
                # perform verification checks
                if ('groupid' not in js or 
                        'rtypeid' not in js or 
                        'start_date' not in js or 
                        'end_date' not in js):
                    continue
                # get request info
                groupid = int(js['groupid'])
                rtypeid = int(js['rtypeid'])
                start_date = int(js['start_date'])
                end_date = int(js['end_date'])
                # get stats info from the database
                resp = dict()
                resp['cmd'] = 'RESP_SENSOR_STATS'
                resp['stats'] = await request.app['db'].stats_sensor(sensorid, 
                    groupid, rtypeid, start_date, end_date)
                # send the response to the client
                await ws.send_str(simplejson.dumps(resp))
        elif msg.type == aiohttp.WSMsgType.ERROR:
            ws.send_str('WebSocket encountered an error: %s\nPlease refresh the page.'.format(ws.exception()))
    
    await _leave(request.app['rooms'], sensorid, ws)

    return ws
    
    
async def socket_shutdown_handler(app):
    """Defines a handler for shutting down any connected WebSockets when the 
    server goes down.
    
    Args:
        app (aiohttp.web.Application): The web application hosting the sensor rooms.
    """
    # close any open websockets
    for sensor in app['rooms'].keys():
        for ws in app['rooms'][sensor].keys():
            if not ws.closed:
                # close the WebSocket
                await ws.close(code=aiohttp.WSCloseCode.GOING_AWAY,
                       message='Server shutdown')
