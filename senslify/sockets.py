import asyncio, dataclasses, queue, typing
import aiohttp
import simplejson


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
    

    def __init__(self, maxsize=256, delay=500):
        '''
        Returns a new instance of a room object.
        '''
        self.__clients = set()
        self.__q = queue.PriorityQueue(maxsize=256)
        self.__delay = delay
        # creates the broadcast loop and schedules it
        self.__loop = asyncio.new_event_loop()
        self.__handle = self.__loop.call_soon(self.__broadcast)
        
        
    def __contains__(self, ws):
        '''
        Defines the contains method so users of the room may make use of the 'in'
        keyword in their implementations.
        Arguments:
            ws: The WebSocket to check for.
        '''
        return ws in self.__clients


    async def __broadcast(self):
        '''
        Defines a task for broadcasting messages to subscribed WebSockets.
        '''
        while self.__broadcasting:
            for ws in self.__clients:
                data = self.__q.get()
                await ws.send_str(simplejson.dumps(data.item))
            await asyncio.sleep(1/self.__delay)
            
    
    @staticmethod
    async def new():
        '''
        Factory function for returning a new room.
        
        Call this fucntion to get a new instance of this class.
        '''
        pass


    async def join(self, ws):
        '''
        Defines a method for subscribing WebSockets to receive messages from this
        room.
        '''
        if ws not in self.__clients:
            self.__clients.add(ws)


    async def leave(self, ws):
        '''
        Defines a method for unsubscribing WebSockets from receiving messages.
        '''
        if ws in self.__clients:
            self.__clients.remove(ws)


    async def receive(self, reading):
        '''
        Enqueues an item to the message queue.
        Arguments:
            reading: A dictionary containing reading information.
        '''
        ts = reading['ts']
        self.__q.put(_PrioritizedItem(ts, reading))
        
        
    def broadcasting(self):
        '''
        Returns whether or not the room is broadcasting messages to its
        participants.
        '''
        return self.__handle.cancelled()
        
        
    def start(self):
        '''
        Starts broadcasting messages.
        '''
        if self.__handle.cancelled():
            self.__handle = self.__loop.call_soon(self.broadcast)
        
        
    def stop(self):
        '''
        Stops broadcasting messages.
        '''
        if not self.__handle.cancelled():
            self.__handle.cancel()


# The way this module is setup may necessitate switching to a class-based view
# Maps sensors to rooms
_rooms = dict()


# Defines a GET handler for WebSockets
async def ws_handler(request):
    global _rooms

    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            js = simplejson.loads(msg.data)
            sensor = js['sensor']
            if js['cmd'] == 'JOIN':
                if sensor not in _rooms.keys():
                    _rooms[sensor] = Room()
                await _rooms[sensor].join(ws)
            # close the connection if the client requested it
            if js['cmd'] == 'CLOSE':
                # remove the client from the sensors room
                _rooms[js['sensor']].leave(ws)
                # close the connection
                await ws.close()
        elif msg.type == aiohttp.WSMsgType.ERROR:
            # TODO: Optimize this, there has to be a better way then iterating
            #   over all the rooms.
            for room in _rooms:
                if ws in room:
                    await room.leave(ws)
                    break
            ws.send_str('WebSocket encountered an error: %s\nPlease refresh the page.'.format(ws.exception()))

    return ws
