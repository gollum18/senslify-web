# Name: sockets.py
# Since: ~Jul. 20th, 2019
# Author: Christen Ford
# Description: Defines a handler for the info page WebSocket as well as various
#   helper functions.

import asyncio, aiohttp
import simplejson


# Define WebSocket command methods


def _does_room_exist(rooms, sensorid):
    '''
    '''
    if not sensorid in rooms:
        return False
    return True


def _does_ws_exist(rooms, sensorid, ws):
    '''
    '''
    if not _does_room_exist(rooms, sensorid):
        return False
    if ws not in rooms[sensorid]:
        return False
    return True    


async def _leave(rooms, sensorid, ws):
    '''
    Allows a WebSocket to leave a room
    '''
    # only delete the ws from the room if room exists and the ws is in the room
    if not _does_ws_exist(rooms, sensorid, ws):
        return
    del rooms[sensorid][ws]


async def _join(rooms, sensorid, ws):
    '''
    Allows a WebSocket to join a room.
    '''
    # create the room if it does not exist
    if sensorid not in rooms:
        rooms[sensorid] = dict()
    # add the client to the room if its not already there, default to temp
    if ws not in rooms[sensorid]:
        rooms[sensorid][ws] = 0


async def _change_stream(rooms, sensorid, ws, rtype):
    '''
    Changes the RType for a connected WebSocket
    '''
    # check if the ws exists, return if so
    if not _does_ws_exist(rooms, sensorid, ws):
        return
    rooms[sensorid][ws] = rtype
    
    
async def message(rooms, sensorid, msg):
    '''
    Sends a message to the participants of a room.
    '''
    # only send the message if the room exists
    if not _does_room_exist(rooms, sensorid):
        return
    # add the command to the message
    msg['cmd'] = 'READING'
    # get the rtype, so we only send to clients that ask for it specifically
    rtypeid = msg['rtypeid']
    msg_str = simplejson.dumps(msg)
    # steps through all clients in the room
    for ws, rtype in rooms[sensorid].items():
        # if the rtypes match up then send the message
        if rtype == rtypeid:
            await ws.send_str(msg_str)


# Defines the handler for the info page WebSocket
async def ws_handler(request):
    '''
    Handles request for the servers websocket address.
    Arguments:
        request: The request that initiated the WebSocket connection.
    '''
    ws = aiohttp.web.WebSocketResponse(autoclose=False, heartbeat=3)
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            js = simplejson.loads(msg.data)
            cmd = js['cmd'];
            sensorid = js['sensorid']
            if cmd == 'JOIN':
                await _join(request.app['rooms'], sensorid, ws)
            # close the connection if the client requested it
            elif cmd == 'CLOSE':
                await _leave(request.app['rooms'], sensorid, ws)
                await ws.close()
                break
            # handler for rtype switch command
            if cmd == 'STREAM':
                await _change_stream(request.app['rooms'], sensorid, ws, js['rtypeid'])   
        elif msg.type == aiohttp.WSMsgType.ERROR:
            ws.send_str('WebSocket encountered an error: %s\nPlease refresh the page.'.format(ws.exception()))
            
    print('RETURNING SOCKET HANDLER')

    return ws
    
    
async def socket_shutdown_handler(app):
    '''
    Defines a handler for shutting down any connected WebSockets when the 
    server goes down.
    Arguments:
        app: The web application hosting the WebSocket rooms.
    '''
    for sensorid in app['rooms'].keys():
        for ws in app[sensorid].keys():
            if not ws.closed:
                await ws.close(code=aiohttp.WSCloseCode.GOING_AWAY,
                    message='Server shutdown!')

