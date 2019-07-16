import aiohttp, aiomongo, pymongo
import bson
import config


# acts as a routing table for the servers endpoints
routes = aiohttp.web.routeTableDef()


# defines an endpoint for the index page
@routes.get('/')
async def index(request):
    # get the sensors from the database
    sensors = await get_sensors(request)
    # construct the responses html body
    d = '''
        '''
    # return the html to the caller
    return aiohttp.web.Response(d)


# defines an endpoint for uploading sensor data
@routes.post('/upload')
async def upload(request):
    await add_reading(request)


# declare a routine for adding readings to the database
async def add_reading(request):
    # holds error information
    error = None
    # TODO: Validate that the sensor data is in proper format
    data = await request.json(loads=bson.loads)
    # check the sensor data before hand
    if not error:
        with (await request.app['database']) as conn:
            # get the database
            db = conn['senslify']
            # insert the data into the database
            try:
                # see if the sensor exists in the database
                if (await db['sensors'].find_one({}))
                    # if so see if its deployment has changed
                        # if the deployment has changed, insert the sensor with its
                        #   deployment
                # if the sensor does not exist in the database, then insert the
                #   sensor add the reading to the database
                await db['readings'].insert_one(simplejson.dumps(data))
                # send data to any connected web sockets registered with the sensor
            except pymongo.errors.PyMongoError:
                error = 'An internal server error has occurred!'

    # check if an error was generated
    if not error:
        return aiohttp.web.Response(text='Sensor reading uploaded successfully.')
    else:
        return aiohttp.web.Response(text=error, status=501)


# defines a routine for getting sensors from the database



# create the web app and run it
app = aiohttp.web.Application()
# setup any necessary configuration stuff
app['database'] = await aiomongo.MongoClient()
# add in the routing table
app.add_routes(routes)
# add in thr routing table
aiohttp.web.run_app(app)
