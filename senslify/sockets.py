import asyncio, dataclass, queue, typing
import aiohttp
import simplejson


class Room:
    '''
    Defines a class that simulates Socket.IO's concept of rooms.

    A room contains a collection of connected aio.http.WebSocket objects.
    '''

    @dataclass.dataclass(order=True)
    class _PrioritizedItem:
        '''
        Defines a class for prioritizing objects.
        '''
        priority: float
        item: typing.Any=dataclass.field(compare=False)

    def __init__(self, maxsize=256, delay=500):
        '''
        Returns a new instance of a room object.
        '''
        self.__clients = set()
        self.__q = queue.PriorityQueue(maxsize=256)
        self.__delay = delay
        # creates the broadcast loop and schedules it
        self.__loop = asyncio.create_event_loop()
        self.__btask = self.__loop.create_task(self.__broadcast())


    async def __broadcast(self):
        '''
        Defines a task for broadcasting messages to subscribed WebSockets.
        '''
        while True:
            for ws in self.__clients:
                data = self.__q.get()
                await ws.send_str(simplejson.dumps(data.item))
            yield from asyncio.sleep(1/self.__delay)


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


    def stop(self):
        '''
        Stops broadcasting messages.
        '''
        if not self.__btask.cancelled():
            self.__btask.cancel()


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
            if js['cmd'] == 'JOIN':
                if not js['sensor'] in _rooms:
                    _rooms['sensor'] = Room()
                _rooms[js['sensor']].join(ws)
            # close the connection if the client requested it
            if js['cmd'] == 'CLOSE':
                # remove the client from the sensors room
                _rooms[js['sensor']].leave(ws)
                # close the connection
                await ws.close()
        elif msg.type == aiohttp.WSMsgType.ERROR:
            # TODO: Inform the client there was an error and close the connection
            pass

    return ws
