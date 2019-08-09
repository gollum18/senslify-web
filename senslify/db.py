# Name: db.py
# Since: ~July 15th, 2019
# Author: Christen Ford
# Description: Encapsulates methods and classes used to interact with the
#   backing database. This module comes packaged with a generic DatabaseProvider
#   as well as a MongoProvider class that implements it. If you want to switch
#   to a different database provider, you should inherit from the
#   DatabaseProvider class and implement its methods. The DatabaseProvider
#   class does not define a __init__ method. Many of the methods in defined
#   by the DatabaseProvider class are asynchronous. As such, you will need
#   to utilize an async compatible database connector when inheriting 
#   from the class.
# The MongoProvider class utilizes provides implementations of the
#   DatabaseProvider methods in the context of MongoDB and is the default
#   provider for the Senslify web application.

# TODO: A request came in to implement human readable names for groups instead
#   of numeric id's, but I don't think I can reasonably accomodate it
#   this far into the project. If a future maintainer wants to handle it
#   you're welcome to do so - CF
# TODO: Also note that the database is intentionally unsecured. Future 
#   future maintainers *should* (shall) implement security on the database
#   side before releasing this software into production. I have made reasonable
#   attempts in the MongoProvider class to prevent ridiculous values from being
#   inserted into the database via the 'upload_handler' but I can't account
#   for all possible situations - CF


import pymongo

from senslify import verify


class DatabaseProvider:
    '''
    Defines a generic database interface. Classes should derive from this
    interface and implement its methods in order to provide an alternative
    '''
    
    # The batch size to use when inserting
    BATCH_SIZE = 100
    
    # The number of documents to return in a single database call
    DOC_LIMIT= 100
    
    
    def init(self):
        '''
        Initializes the database with the initial table design dictated in
        'Docs/DB.md'. This command should either fail soft or prompt the user
        to confirm deletion of the database if the database already exists.
        '''
        raise NotImplementedError
        
        
    async def does_group_exist(self, groupid):
        '''
        Determines if the specifiied group exists in the database.
        Arguments:
            groupid: The id of the group to check for.
        '''
        raise NotImplementedError
        
        
    async def does_rtype_exist(self, rtypeid):
        '''
        Determines if the specified sensor exists in the database.
        Arguments:
            rtypeid: The id of the rtype to check for.
        '''
        raise NotImplementedError
        
        
    async def does_sensor_exist(self, sensorid, groupid):
        '''
        Determines if the specified sensor exists in the database.
        Arguments:
            sensorid: The id of the sensor to check for.
            groupid: The id of the group the sensor belongs to.
        '''
        raise NotImplementedError
        
        
    async def get_groups(self):
        '''
        Generator function used to get groups from the database.
        '''
        raise NotImplementedError
    
    
    async def get_rtypes(self):
        '''
        Generator function used to get reading types from the database.
        '''
        raise NotImplementedError
    
    
    async def get_sensors(self, groupid):
        '''
        Generator function used to get sensors from the database.
        Arguments:
            groupid: The id of the group to return sensors from.
        '''
        raise NotImplementedError
        
    
    async def get_readings(self, sensorid, groupid, limit=DOC_LIMIT):
        '''
        Generator function for retrieving readings from the database.
        Arguments:
            sensorid: The id of the sensor to return readings on.
            groupid: The id of the group the sensor belongs to.
            limit: The number of readings to return in a single call.
        '''
        raise NotImplementedError
        
        
    async def insert_group(self, groupid):
        '''
        Inserts a group into the database.
        Arguements:
            groupid: The id of the group.
        '''
        raise NotImplementedError
        
        
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
        raise NotImplementedError
        
        
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
        raise NotImplementedError
        
        
    async def insert_sensor(self, sensorid, groupid):
        '''
        Inserts a sensorboard into the database.
        Arguments:
            sensorid: The id assigned to the sensorboard.
            groupid: The id of the group the sensorboard belongs to.
        '''
        raise NotImplementedError


class MongoProvider(DatabaseProvider):
    '''
    Represents a unique connection to a MongoDB instance. Each instance of
    this class represents an individual connection to the MongoDB database.
    
    The functions in this class are asynchronous. To acheive this, I employ
    gevent and monkey patching. That said, at any time, the result of any
    of these functions are not guaranteed to be accurate reflections of the
    database (not that they would anyway - in reality, unless a Session object
    is used, MongoDB only provides atomicity at the collection level).
    
    I chose this approach rather than utilizing Motor or aiomongo because
    the former is too heavy for this application and introduces additional
    complexity, while the former is not up to date with the latest PyMongo
    driver.
    '''
    
    
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
        print('Initializing database...')
        if self._db in self._conn.list_database_names():
            if input('Senslify Database detected, do you want to delete it? [y|n]: ').lower() == 'y':
                print('Warning: Deleting Senslify database!')
                try:
                    self._conn.drop_database(self._db)
                except pymongo.errors.ConnectionFailure as e:
                    raise e
                except pymongo.errors.PyMongoError as e:
                    raise e
            else:
                # otherwise exit the method, no initialization needed
                return
        # create the indexes on the collections in the database
        self._conn[self._db].sensors.create_index([
            ("sensorid", pymongo.ASCENDING),
            ("groupid", pymongo.ASCENDING)], unique=True
        )
        self._conn[self._db].groups.create_index([
            ("groupid", pymongo.ASCENDING)], unique=True
        )
        self._conn[self._db].rtypes.create_index([
            ("rtypeid", pymongo.ASCENDING),
            ("rtype", pymongo.ASCENDING)], unique=True
        )
        self._conn[self._db].readings.create_index([
            ("sensorid", pymongo.ASCENDING),
            ("groupid", pymongo.ASCENDING),
            ("rtypeid", pymongo.ASCENDING),
            ("ts", pymongo.ASCENDING)], unique=True
        )
        # insert starting rtypes into the database
        #   if you want more rtypes in the database than this, you'll need to
        #   insert them through the Mongo shell, I don't provide a way to do so
        # or you know, you could modify this list too, but it will require 
        #   reinitializing the database, deleting anything in there currently
        self._conn[self._db].rtypes.insert_many([
            # Note that these rtypes match up with the ReadForward TOS App
            {"rtypeid": 0, "rtype": "Temperature"},
            {"rtypeid": 1, "rtype": "Humidity"},
            {"rtypeid": 2, "rtype": "Visible Light"},
            {"rtypeid": 3, "rtype": "Infrared Light"},
            {"rtypeid": 4, "rtype": "Voltage"}
        ])
            
            
    async def does_group_exist(self, groupid, deployment):
        '''
        Determines if the specifiied group exists in the database.
        Arguments:
            groupid: The id of the group to check for.
            deployment: The deployment of the group.
        '''
        try:
            return self._conn[self._db].groups.find_one(
                filter={'groupid': groupid}) is not None
        except pymongo.errors.ConnectionFailure as e:
            raise e
        except pymongo.errors.PyMongoError as e:
            raise e
        
        
    async def does_rtype_exist(self, rtypeid):
        '''
        Determines if the specified sensor exists in the database.
        Arguments:
            rtypeid: The id of the rtype to check for.
        '''
        try:
            return self._conn[self._db].rtypes.find_one(
                filter={'rtypeid': rtypeid}) is not None
        except pymongo.errors.ConnectionFailure as e:
            raise e
        except pymongo.errors.PyMongoError as e:
            raise e
        
    
    async def does_sensor_exist(self, sensorid, groupid):
        '''
        Determines if the specified sensor exists in the database.
        Arguments:
            sensorid: The id of the sensor to check for.
        '''
        try:
            return self._conn[self._db].sensors.find_one(
                    filter={'sensorid': sensorid,
                            'groupid': groupid}) is not None
        except pymongo.errors.ConnectionFailure as e:
            raise e
        except pymongo.errors.PyMongoError as e:
            raise e


    async def get_groups(self):
        '''
        Generator function used to get groups from the database.
        Arguments:
            batch_size: The number of groups to return in each batch.
        '''
        try:
            with self._conn[self._db].groups.find() as cursor:
                for doc in cursor:
                    yield doc
        except pymongo.errors.ConnectionFailure as e:
            raise e
        except pymongo.errors.PyMongoError as e:
            raise e


    async def get_readings(self, sensorid, groupid, 
            limit=DatabaseProvider.DOC_LIMIT):
        '''
        Generator function for retrieving readings from the database.
        Arguments:
            sensorid: The id of the sensor to return readings on.
            groupid: The id of the group the sensor belongs to.
            limit: The number of readings to return in a single call.
        '''
        try:
            # TODO: Only want to select the most recent readings
            with self._conn[self._db].readings.find(
                    filter={'sensorid': sensorid, 
                            'groupid': groupid}).limit(limit) as cursor:
                for doc in cursor:
                    yield doc
        except pymongo.errors.ConnectionFailure as e:
            raise e
        except pymongo.errors.PyMongoError as e:
            raise e
        
        
    async def get_rtypes(self):
        '''
        Generator function used to get reading types from the database.
        Arguments:
            batch_size: The number of reading types to return in each batch.
        '''
        try:
            with self._conn[self._db].rtypes.find(
                    batch_size=batch_size) as cursor:
                for batch in cursor:
                    yield batch
        except pymongo.errors.ConnectionFailure as e:
            raise e
        except pymongo.errors.PyMongoError as e:
            raise e


    async def get_sensors(self, groupid):
        '''
        Generator function used to get sensors from the database.
        Arguments:
            groupid: The id of the group to return sensors from.
            batch_size: The number of sensors to return in a single batch.
        '''
        try:
            with self._conn[self._db].sensors.find(
                    filter={'groupid': groupid}) as cursor:
                for doc in cursor:
                    yield doc
        except pymongo.errors.ConnectionFailure as e:
            raise e
        except pymongo.errors.PyMongoError as e:
            raise e
        
        
    async def insert_group(self, groupid):
        '''
        Inserts a group into the database.
        Arguements:
            groupid: The id of the group.
        '''
        try:
            if not self.does_group_exist(groupid):
                self._conn[self._db].insert_one({"groupid": groupid})
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
            sensorid = reading['sensorid']
            groupid = reading['groupid']
            deployment = reading['deployment']
            # insert the sensor if it does not exist
            if not await self.does_sensor_exist(sensorid, groupid):
                await self.insert_sensor(sensorid, groupid)
            # #TODO: insert the group if it does not exist
            if not await self.does_group_exist(groupid):
                await self.insert_group(groupid)
            # make sure that the rtype exists, exit otherwise
            if not await self.does_rtype_exist(rtypeid):
                return
            # insert the reading into the database
            self._conn[self._db].insert_one(reading)
        except pymongo.errors.ConnectionFailure as e:
            return False, e
        except pymongo.errors.PyMongoError as e:
            return False, e
        return True, None
        
        
    async def insert_readings(self, readings, batch_size=DatabaseProvider.BATCH_SIZE):
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
        #TODO: Some sort of verification needs performed on the readings
        #   maybe we can only insert readings that verify? idk for now
        if not map(verify.verify_reading, readings):
            return False, None
        try:
            index = 0
            lim = len(readings)
            while step < lim:
                step = batch_size if index + batch_size < lim else lim - index
                self._conn[self._db].insert_many(readings[index:index+step])
                index += step
        except pymongo.errors.ConnectionFailure as e:
            return False, e
        except pymongo.errors.PyMongoError as e:
            return False, e
        return True, None
        
        
    async def insert_sensor(self, sensorid, groupid):
        '''
        Inserts a sensorboard into the database.
        Arguments:
            sensorid: The id assigned to the sensorboard.
            groupid: The id of the group the sensorboard belongs to.
        '''
        try:
            self._conn[self._db].insert_one({'sensorid': sensorid, 'groupid': groupid})
        except pymongo.errors.ConnectionFailure as e:
            return False, e
        except pymongo.errors.PyMongoError as e:
            return False, e
