import pymongo

from senslify import verify


class MongoDBConn:
    '''
    Represents a unique connection to a MongoDB instance.
    '''
    
    
    BATCH_SIZE = 100
    
    
    def __init__(self, conn_str='mongodb://0.0.0.0:27001', db='senslify'):
        '''
        Returns an object capable of interacting with the Senslify MongoDB
        database.
        '''
        self._conn = pymongo.MongoClient(conn_str)
        self._db = db
        
        
    def init(self):
        '''
        Initializes the database with the initial table design dictated in
        'Docs/DB.md'. This command will fail-soft if the database already 
        exists.
        '''
        pass
    
    
    async def does_sensor_exist(self, sensorid):
        '''
        Determines if the specified sensor exists in the database.
        Arguments:
            sensorid: The id of the sensor to check for.
        '''
        try:
            return self._conn[self._db].senslify.readings.find_one(
                    filter={'sensorid': sensorid}) is not None, e
        except pymongo.errors.ConnectionFailure as e:
            return False, e
        except pymongo.errors.PyMongoError as e:
            return False, e
            
            
    async def does_group_exist(self, groupid):
        '''
        Determines if the specifiied group exists in the database.
        Arguments:
            groupid: The id of the group to check for.
        '''
        try:
            return self._conn[self._db].senslify.groups.find_one(
                    filter={'group': groupid}) is not None, None
        except pymongo.errors.ConnectionFailure as e:
            return False, e
        except pymongo.errors.PyMongoError as e:
            return False, e


    async def get_groups(self, batch_size=BATCH_SIZE):
        '''
        Generator function used to get groups from the database.
        Arguments:
            batch_size: The number of groups to return in each batch.
        '''
        try:
            with self._conn[self._db].senslify.groups.find(batch_size=batch_size) as cursor:
                for batch in cursor:
                    yield batch
        except pymongo.errors.ConnectionFailure as e:
            raise e
        except pymongo.errors.PyMongoError as e:
            raise e
        
        
    async def get_rtypes(self, batch_size=BATCH_SIZE):
        '''
        Generator function used to get reading types from the database.
        Arguments:
            batch_size: The number of reading types to return in each batch.
        '''
        try:
            with self._conn[self._db].senslify.rtypes.find(batch_size=batch_size) as cursor:
                for batch in cursor:
                    yield batch
        except pymongo.errors.ConnectionFailure as e:
            raise e
        except pymongo.errors.PyMongoError as e:
            raise e


    async def get_sensors(self, groupid, batch_size=BATCH_SIZE):
        '''
        Generator function used to get sensors from the database.
        Arguments:
            groupid: The id of the group to return sensors from.
            batch_size: The number of sensors to return in a single batch.
        '''
        try:
            with self._conn[self._db].senslify.readings.find(
                    filter={'groupid': groupid}, 
                    projection={}, 
                    batch_size=batch_size) as cursor:
                for batch in cursor:
                    yield batch
        except pymongo.errors.ConnectionFailure as e:
            raise e
        except pymongo.errors.PyMongoError as e:
            raise e


    async def get_readings(self, sensorid, groupid, batch_size=BATCH_SIZE, 
            limit=BATCH_SIZE):
        '''
        Generator function for retrieving readings from the database.
        Arguments:
            sensorid: The id of the sensor to return readings on.
            groupid: The id of the group the sensor belongs to.
            limit: The number of readings to return in a single call.
        '''
        try:
            # TODO: Only want to select the most recent readings
            with self._conn[self._db].senslify.readings.find(
                    filter={'sensorid': sensorid, 
                            'groupid': groupid}).limit(limit) as cursor:
                for batch in cursor:
                    yield batch
        except pymongo.errors.ConnectionFailure as e:
            raise e
        except pymongo.errors.PyMongoError as e:
            raise e


    async def insert_reading(self, reading):
        '''
        Inserts a single reading into the database.
        Arguments:
            reading: The reading to insert into the database, should be a
            Python dict object.
        Returns:
            A pair in the form (result, reason) where:
                result: A boolean, whether the documents were inserted.
                reason: An exception if an exception occurred.
        '''
        # only insert if the reading contains a sensor and group
        if not verify.verify_reading(reading):
            return False, None
        try:
            self._conn[self._db].insert_one(reading)
        except pymongo.errors.ConnectionFailure as e:
            return False, e
        except pymongo.errors.PyMongoError as e:
            return False, e
        return True, None
        
        
    async def insert_readings(self, readings, batch_size=BATCH_SIZE):
        '''
        Inserts multiple readings into the database.
        Arguments:
            readings: A list of readings to insert into the database, should be
            a Python dict object.
            batch_size: The amount of readings to insert per batch.
        Returns:
            A pair in the form (result, reason) where:
                result: A boolean, whether the documents were inserted.
                reason: An exception if an exception occurred.
        '''
        if not map(verify.verify_reading, readings):
            return False, None
        try:
            index = 0
            lim = len(readings)
            while step < lim:
                step = batch_size if index + batch_size < lim else lim
                self._conn[self._db].insert_many(readings[index:index+step])
                index += step
        except pymongo.errors.ConnectionFailure as e:
            return False, e
        except pymongo.errors.PyMongoError as e:
            return False, e
        return True, None
