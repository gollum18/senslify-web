import asyncio, dataclasses, queue, typing
import aiohttp
import simplejson


# The way this module is setup may necessitate switching to a class-based view
# Maps sensors to rooms
_rooms = dict()


class Room:
    '''
    Defines a class that simulates Socket.IO's concept of rooms.

    A room contains a collection of connected aio.http.WebSocket objects.
    '''

    @dataclasses.dataclass(order=True)
    class _PrioritizedItem:
        '''
        Defines a class for prioritizing objects.
        '''
        priority: float
        item: typing.Any=dataclasses.field(compare=False)
        
        
    def __contains__(self, ws):
        '''
        Defines the contains method so users of the room may make use of the 'in'
        keyword in their implementations.
        Arguments:
            ws: The WebSocket to check for.
        '''
        
        return ws in self._clients


    async def __broadcast(self):
        '''
        Defines a task for broadcasting messages to subscribed WebSockets.
        '''
        while True:
            data = self._q.get()
            # the actual reading is stored in the item field
            #   informs the client that the pkt is a reading
            data.item['cmd'] = 'READING'
            for ws in self._clients:
                await ws.send_str(simplejson.dumps(data.item))
            await asyncio.sleep(1/self._delay)
            
            
    def is_empty(self):
        '''
        Determines if the room is empty or not.
        '''
        return len(self.__clients) == 0
            
    
    @staticmethod
    async def new(maxsize=256, delay=500):
        '''
        Factory function for returning a new room.
        
        Call this function to get a new instance of this class.
        '''
        room = Room()
        room._clients = set()
        room._q = queue.PriorityQueue(maxsize=256)
        room._delay = delay
        # creates the broadcast loop and schedules it
        room._loop = asyncio.new_event_loop()
        room._btask = await self._loop.create_task(self.__broadcast())
        # return the room
        return room
    

    async def join(self, ws):
        '''
        Defines a method for subscribing WebSockets to receive messages from this
        room.
        '''
        if not self.contains(ws):
            self._clients.add(ws)


    async def leave(self, ws):
        '''
        Defines a method for unsubscribing WebSockets from receiving messages.
        '''
        if ws in self._clients:
            self._clients.remove(ws)


    async def receive(self, msg):
        '''
        Enqueues an item to the message queue.
        Arguments:
            msg: A dictionary containing reading information.
        '''
        ts = msg['ts']
        self.__q.put(_PrioritizedItem(ts, msg))
        
        
    def broadcasting(self):
        '''
        Returns whether or not the room is broadcasting messages to its
        participants.
        '''
        return self.__handle.cancelled()
        
        
    async def start(self):
        '''
        Starts broadcasting received messages to WebSockets in the room.
        '''
        if self._btask.cancelled():
            self._btask = await self._loop.create_task(self.__broadcast())


    def stop(self):
        '''
        Stops broadcasting messages.
        '''
        if not self._btask.cancelled():
            self._btask.cancel()


async def message(room, msg):
    '''
    Messages a room.
    
    This method is called externally from the upload handler in the sensors.py
    file. Do not call this method directly from this class.
    Arguments:
        room: The room to message.
        msg: The message itself.
    '''
    global _rooms
    
    if room in _rooms.keys():
        if not _rooms[room].is_empty():
            await _rooms[room].receive(msg)


# Defines a GET handler for WebSockets
async def ws_handler(request):
    '''
    Handles request for the servers websocket address.
    Arguments:
        request: The request that initiated the WebSocket connection.
    '''
    global _rooms

    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            js = simplejson.loads(msg.data)
            cmd = js['cmd'];
            sensorid = js['sensorid']
            if cmd == 'JOIN':
                if sensorid not in _rooms.keys():
                    _rooms[sensorid] = Room()
                await _rooms[sensorid].join(ws)
            # close the connection if the client requested it
            elif cmd == 'CLOSE':
                # remove the client from the sensors room
                await _rooms[sensorid].leave(ws)
                # close the connection
                await ws.close()
            # handler for rtype switch command
            if cmd == 'STREAM':
                # TODO: Update the rtype for the socket
                pass
        elif msg.type == aiohttp.WSMsgType.ERROR:
            for room in _rooms:
                # this is an O(1) operation, so this should be fine
                if ws in room:
                    await room.leave(ws)
                    break
            ws.send_str('WebSocket encountered an error: %s\nPlease refresh the page.'.format(ws.exception()))

    return ws
