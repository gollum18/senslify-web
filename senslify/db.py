# THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
# APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
# HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT
# WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
# PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE
# DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR ORb
# CORRECTION.

# Name: db.py
# Since: ~July 15th, 2019
# Author: Christen Ford
# Description: Encapsulates methods and classes used to interact with the
#   backing database. This class provides a generic database adapater that
#   includes a set of basic functionality needed by the Senslify web
#   application. This adapter serves as a base class for driver specific
#   implementations of the adapter. The list of drivers that this application
#   supports out-of-the-box are listed below.

# The list of supported (non 3rd party) drivers are:
# The MongoProvider class provides implementations of the
#   DatabaseProvider methods in the context of MongoDB and is the default
#   provider for the Senslify web application.
# The PostGresProvider class provides implementations of the 
#   DatabaseProvider methods in the context of PostGresSQL and is a secondary
#   provider for the Senslify web application.
# The SQLServerProvider class provides implementations of the 
#   DatabaseProvider methods in the context of Microsoft SQL Server and is
#   a secondary provider for the Senslify web application.


import bson, pymongo, pyodbc, sys
from contextlib import contextmanager
from senslify.errors import DBError


async def database_shutdown_handler(app):
    """Defines a handler for gracefully shutting down the application database.

    Args:
        app (aiohttp.web.Application): An instance of the Senslify application.
    """
    if 'db' in app:
        await app['db'].close()
        del app['db']


class DatabaseProvider:
    """Defines a generic database interface. Classes should derive from this
    interface and implement its methods in order to provide an alternative
    """

    # The batch size to use when inserting
    BATCH_SIZE = 100

    # The number of documents to return in a single database call
    DOC_LIMIT= 100


    def __init__(self, conn_str, db):
        """Returns an instance of a DatabaseProvider. Do not call this function.
        All of the methods defined by the DatabaseProvider class will raise a
        NotImplementedError when called.

        Args:
            conn_str (str): The connection string for the database server.
            db (str): The name of the Senslify database.
        """
        self._conn_str = conn_str
        self._db = db
        self._open = False


    @staticmethod
    @contextmanager
    def get_connection(conn_str, db):
        """Gets a connection to the backing database server.

        This method shall be implemented as a generator function, shall yield
        an instance of a DatabaseProvider, and shall close the provider when
        done.

        Args:
            conn_str (str): The connection string to the database server.
            db (str): The name of the Senslify database.

        Returns:
            DatabaseProvider: A temporary database provider.
        """
        raise NotImplementedError


    async def close(self):
        """Closes the connection to the backing database provider."""
        raise NotImplementedError


    def init(self, migration):
        """Initializes the database with the initial table design dictated in
        'Docs/DB.md'.

        This command should either fail soft or prompt the user
        to confirm deletion of the database if the database already exists.

        Arguments:
            migration (boolean): Whether the database is a migration database
            or not.
        """
        raise NotImplementedError


    async def delete_group(self, groupid):
        """Deletes the indicated group from the database. This operation cascades
        to sensors and readings.

        Args:
            groupid (int): A group identifier.

        Returns:
            (int): The number of records that are deleted.
        """
        raise NotImplementedError


    async def delete_reading(self, sensorid, groupid, rtypeid, ts):
        """Deletes the indicated reading from the database.

        Args:
            sensorid (int): A sensor identifier.
            groupid (int): A group identifier.
            rtypeid (int): A reading type identifier.
            ts (int): A UNIX timestamp.

        Returns:
            (int): The number of records that are deleted.
        """
        raise NotImplementedError


    async def delete_readings(self, sensorid, groupid, rtypeid=None):
        """Deletes all readings for the indicated sensor. if rtypeid is not
        None, only deletes readings that match the specified reading type.

        Args:
            sensorid (int): A sensor identifier.
            groupid (int): A group identifier.
            rtypeid (int): A reading type identifier (default: None).

        Returns:
            (int): The number of records that are deleted. 
        """
        raise NotImplementedError


    async def delete_rtype(self, rtypeid):
        """Deletes the indicated rtype from the database. This operation 
        cascades to readings.

        Args:
            rtypeid (int): A reading type identifier.

        Returns:
            (int): The number of records that are deleted.
        """
        raise NotImplementedError


    async def delete_sensor(self, groupid, sensorid):
        """Deletes the indicated sensor from the database. This operation
        cascades to readings.

        Args:
            groupid (int): A group identifier.
            sensorid (int): A sensor identifier.

        Returns:
            (int): The number of records that are deleted.
        """
        raise NotImplementedError


    async def does_group_exist(self, groupid):
        """Determines if the specifiied group exists in the database.

        Args:
            groupid (int): The id of the group to check for.

        Returns:
            (boolean): True if the group exists, False otherwise.
        """
        raise NotImplementedError


    async def does_rtype_exist(self, rtypeid):
        """Determines if the specified sensor exists in the database.

        Args:
            rtypeid (int): The id of the rtype to check for.

        Returns:
            (boolean): True if the reading type exists, False otherwise.
        """
        raise NotImplementedError


    async def does_sensor_exist(self, sensorid, groupid):
        """Determines if the specified sensor exists in the database.

        Args:
            sensorid (int): The id of the sensor to check for.
            groupid (int): The id of the group the sensor belongs to.

        Returns:
            (boolean): True if the sensor sensor exists, False otherwise.
        """
        raise NotImplementedError


    async def find_max_groupid(self):
        '''Determines the maximum groupid stored in the database.'''
        raise NotImplementedError


    async def find_max_sensorid_in_group(self, groupid):
        '''Determines the maximum sensor identifier stored in the database for the 
        specified group.

        Arguments:
            groupid (int): A group identifier that the sensor will be provisioned with.
        '''
        raise NotImplementedError


    async def get_groups(self):
        """Generator function used to get groups from the database."""
        raise NotImplementedError


    async def get_rtypes(self):
        """Generator function used to get reading types from the database."""
        raise NotImplementedError


    async def get_sensors(self, groupid):
        """Generator function used to get sensors from the database.

        Args:
            groupid (int): The id of the group to return sensors from.
        """
        raise NotImplementedError


    async def get_readings(self, sensorid, groupid, rtype=None, limit=DOC_LIMIT):
        """Generator function for retrieving readings from the database.

        Args:
            sensorid (int): The id of the sensor to return readings on.
            groupid (int): The id of the group the sensor belongs to.
            rtypeid (int): The id of the rtype corresponding the reading type to return (default: None).
            limit (int): The number of readings to return in a single call (default: 100).
        """
        raise NotImplementedError


    async def insert_group(self, groupid, alias):
        """Inserts a group into the database.

        Args:
            groupid (int): The id of the group.
            alias (str): The human readable alias for the group.
        """
        raise NotImplementedError


    async def insert_reading(self, reading):
        """Inserts a single reading into the database.

        Args:
            reading (dict): The reading to insert into the database.
        """
        raise NotImplementedError


    async def insert_readings(self, readings, batch_size=BATCH_SIZE):
        """Inserts multiple readings into the database.

        Args:
            readings (list): A list of readings to insert into the database.
            batch_size (int): The amount of readings to insert per batch.
        """
        raise NotImplementedError


    async def insert_sensor(self, sensorid, groupid, alias):
        """Inserts a sensorboard into the database.

        Args:
            sensorid (int): The id assigned to the sensorboard.
            groupid (int): The id of the group the sensorboard belongs to.
            alias (str): The human readable alias for the sensor.
        """
        raise NotImplementedError


    def is_open(self):
        return self._open


    def open(self):
        """Opens a connection to the backing database server."""
        raise NotImplementedError


    async def stats_group(self, groupid, rtypeid, start_ts=None, end_ts=None):
        """Returns the stats for an entire group of sensors.

        Args:
            groupid (int): The id of the group the sensor belongs to.
            rtypeid (int): The id of the reading type to retrieve stats for.
            start_ts (datetime.datetime): The start time that begins the range
            for stats (default:None).
            end_ts (datetime.datetime): The end time that ends the range for
            stats (default: None).

        Returns:
            (generator): A Python generator over the stats from the database.

        Raises:
            (Exception): If there was a problem interacting with the database.
        """
        raise NotImplementedError


    async def stats_sensor(self, sensorid, groupid, rtypeid, start_ts, end_ts):
        """Returns the stats for a specific sensor.

        Args:
            sensorid (int): The id of the sensor to retrieve stats on.
            groupid (int): The id of the group the sensor belongs to.
            rtypeid (int): The id of the reading type to retrieve stats for.
            start_date (datetime.datetime): The start time that begins the range
            for stats.
            end_date (datetime.datetime): The end time that ends the range for
            stats.

        Raises:
            (Exception): If there was a problem interacting with the database.
        """
        raise NotImplementedError


    async def get_readings_by_period(self, sensorid, groupid, start_ts, end_ts):
        """Returns all of the readings for a given time period for a given
        sensor.

        Args:
            sensorid (int): The id of the sensor to get readings for.
            groupid (int): The id of the group the sensor belongs to.
            start_ts (datetime.datetime): The start time period.
            end_ts (datetime.datetime): The end time period.
        """
        raise NotImplementedError


class MongoProvider(DatabaseProvider):
    """Represents a unique connection to a MongoDB instance. Each instance of
    this class represents an individual connection to the MongoDB database.

    The functions in this class are asynchronous. To acheive this, I employ
    gevent and monkey patching. That said, at any time, the result of any
    of these functions are not guaranteed to be accurate reflections of the
    database (not that they would anyway - in reality, unless a Session object
    is used, MongoDB only provides atomicity at the collection level).
    """

    # the maximum time in milliseconds that aggregate operations are limited
    #   to running on the server
    MAX_AGGREGATE_MS = 2500

    def __init__(self, conn_str='mongodb://127.0.0.1:27001', db='senslify',
            username=None, password=None):
        """Returns an object capable of interacting with the Senslify MongoDB
        database. You must manually open the connection by calling open()
        on the provider before you can use the providers methods.

        Args:
            conn_str (str): The connection string to the MongoDB server
            (default mongodb://127.0.0.1:27001)
            db (str): The name of the Senslify database (default senslify)
            username (str): The username to connect to the database with (default=None).
            password (str): The password corresponding to the username (default=None).
        """
        DatabaseProvider.__init__(self, conn_str, db)
        # Name mangling is ok, but these should really be stored in encrypted memory
        if username is str and password is str:
            self.__username = str(username)
            self.__password = str(password)
        else:
            self.__username = None
            self.__password = None


    @staticmethod
    @contextmanager
    def get_connection(conn_str, db, username=None, password=None):
        """Generator function that creates a temporary MongoProvider instance to
        be used within a context manager.

        This method shall be implemented as a generator function, shall yield
        an instance of a DatabaseProvider, and shall close the provider when
        done.

        Arguments:
            conn_str (str): The connection string to the MongoDB server.
            db (str): The name of the Senslify database.
            username (str): The username to connect to the database with.
            password (str): The password corresponding to the username.
        """
        conn = MongoProvider(conn_str, db, username, password)
        conn.open()
        yield conn
        conn.close()


    async def close(self):
        """Closes the connection to the backing database provider. Does nothing
        if the connection is not opened.
        """
        if self._open:
            self._conn.close()
            self._open = False


    def init(self, migration=False):
        """Initializes the database with the initial table design dictated in
        'docs/DB.rst'. This command will fail-soft if the database already
        exists.

        Arguments:
            migration (boolean): Whether the database is a migration database
            or not (default: False).
        """
        if not self._open:
            print('Cannot initialize database, connection not open!')
            return
        try:
            if self._db in self._conn.list_database_names():
                if input('Senslify Database detected, do you want to delete it? [y|n]: ').lower() == 'y':
                    print('Warning: Deleting Senslify database!')
                    self._conn.drop_database(self._db)
                    return
                else:
                    # otherwise exit the method, no initialization needed
                    return
            # create the indexes on the collections in the database
            self._conn[self._db].readings.create_index([
                ("sensorid", pymongo.ASCENDING),
                ("groupid", pymongo.ASCENDING),
                ("rtypeid", pymongo.ASCENDING),
                ("ts", pymongo.ASCENDING)], unique=True
            )
            if not migration:
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
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def delete_group(self, groupid):
        """Deletes the indicated group from the database. This operation cascades
        to sensors and readings.

        Args:
            groupid (int): A group identifier.

        Returns:
            (int): The number of records that are deleted.
        """
        if not self._open:
            raise DBError('ERROR: Cannot delete group from database, database connection is not open!')
        count = 0
        try:
            count += self._conn[self._db].readings.delete_many(
                filter={
                    'groupid': groupid
                }
            )
            count += self._conn[self._db].sensors.delete_many(
                filter={
                    'groupid': groupid
                }
            )
            count += self._conn[self._db].groups.delete_one(
                filter={
                    'groupid': groupid
                }
            )
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')
        return count


    async def delete_reading(self, sensorid, groupid, rtypeid, ts):
        """Deletes the indicated reading from the database.

        Args:
            sensorid (int): A sensor identifier.
            groupid (int): A group identifier.
            rtypeid (int): A reading type identifier.
            ts (int): A UNIX timestamp.

        Returns:
            (int): The number of readings that are deleted.
        """
        if not self._open:
            raise DBError('ERROR: Cannot delete reading from database, database connection is not open!')
        try:
            return self._conn[self._db].readings.delete_one(
                filter={
                    'sensorid': sensorid, 
                    'groupid': groupid, 
                    'rtypeid': rtypeid, 
                    'ts': ts
                }
            )
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def delete_readings(self, sensorid, groupid, rtypeid=None):
        """Deletes all readings for the indicated sensor. if rtypeid is not
        None, only deletes readings that match the specified reading type.

        Args:
            sensorid (int): A sensor identifier.
            groupid (int): A group identifier.
            rtypeid (int): A reading type identifier (default: None).

        Returns:
            (int): The number of records that are deleted. 
        """
        if not self._open:
            raise DBError('ERROR: Cannot delete readings from database, database connection is not open!')
        count = 0
        try:
            if rtypeid:
                query={'sensorid': sensorid, 'groupid': groupid, 'rtypeid': rtypeid}
            else:
                query={'sensorid': sensorid, 'groupid': groupid}
            count += self._conn[self._db].readings.delete_many(filter=query)
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')
        return count


    async def delete_rtype(self, rtypeid):
        """Deletes the indicated rtype from the database. This operation 
        cascades to readings.

        Args:
            rtypeid (int): A reading type identifier.

        Returns:
            (int): The number of records that are deleted.
        """
        if not self._open:
            raise DBError('ERROR: Cannot delete reading type from database, database connection is not open!')
        count = 0
        try:
            count += self._conn[self._db].readings.delete_many(
                filter={
                    'rtypeid': rtypeid
                }
            )
            count += self._conn[self._db].rtypes.delete_one(
                filter={
                    'rtypeid': rtypeid
                }
            )
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')
        return count


    async def delete_sensor(self, groupid, sensorid):
        """Deletes the indicated sensor from the database. This operation
        cascades to readings.

        Args:
            groupid (int): A group identifier.
            sensorid (int): A sensor identifier.

        Returns:
            (int): The number of records that are deleted.
        """
        if not self._open:
            raise DBError('ERROR: Cannot delete sensor from database, database connection is not open!')
        count = 0
        try:
            count += self._conn[self._db].readings.delete_many(
                filter={
                    'groupid': groupid, 
                    'sensorid': sensorid
                }
            )
            count += self._conn[self._db].sensors.delete_one(
                filter={
                    'groupid': groupid, 
                    'sensorid': sensorid
                }
            )
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')
        return count


    async def does_group_exist(self, groupid):
        """Determines if the specifiied group exists in the database.

        Args:
            groupid (int): The id of the group to check for.
        """
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists, database connection not open!')
        try:
            return self._conn[self._db].groups.find_one(
                filter={'groupid': groupid}) is not None
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def does_rtype_exist(self, rtypeid):
        """Determines if the specified sensor exists in the database.

        Args:
            rtypeid (int): The id of the rtype to check for.
        """
        if not self._open:
            raise DBError('Cannot determine if rtype exists, database connection not open!')
        try:
            return self._conn[self._db].rtypes.find_one(
                filter={'rtypeid': rtypeid}) is not None
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def does_sensor_exist(self, sensorid, groupid):
        """Determines if the specified sensor exists in the database.

        Args:
            sensorid (int): The id of the sensor to check for.
        """
        if not self._open:
            raise DBError('Cannot determine if sensor exists, database connection not open!')
        try:
            return self._conn[self._db].sensors.find_one(
                    filter={'sensorid': sensorid,
                            'groupid': groupid}) is not None
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def find_max_groupid(self):
        '''Determines the maximum group identifier stored in the database.
        '''
        pipeline = [
            # optimization step - sort descending by group identifier
            {"$sort":
                {"groupid": -1}
            },
            # project just the max sensorid
            {"$project": 
                {"max": {"$max": "$groupid"}}
            }
        ]
        try:
            with self._conn[self._db].groups.aggregate(pipeline,
                allowDiskUse=True, maxTimeMS=self.MAX_AGGREGATE_MS) as cursor:
                doc = cursor.next()
                if not doc: raise DBError
                return doc
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def find_max_sensorid_in_group(self, groupid):
        '''Determines the maximum sensor identifier stored in the database for the 
        specified group.

        Arguments:
            groupid (int): A group identifier that the sensor will be provisioned with.
        '''
        if not self._open:
            raise DBError('Cannot retrieve stats for sensor, database connection not open!')
        groupid = int(groupid)
        pipeline = [
            # filter by sensorid, groupid, and rtypeid
            #   these are all indexed so this should be fast
            {"$match": {
                    "$and": [{
                        "groupid": {"$eq": groupid}
                    }]
                }
            },
            # optimization step - sort descending by sensor identifier
            {"$sort":
                {"sensorid": -1}
            },
            # project just the max sensorid
            {"$project": 
                {"max": {"$max": "$sensorid"}}
            }
        ]
        try:
            with self._conn[self._db].sensors.aggregate(pipeline,
                allowDiskUse=True, maxTimeMS=self.MAX_AGGREGATE_MS) as cursor:
                doc = cursor.next()
                if not doc: raise DBError
                return doc
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def get_groups(self):
        """Generator function used to get groups from the database.

        Args:
            batch_size (int): The number of groups to return in each batch.
        """
        if not self._open:
            raise DBError('Cannot get groups, database connection not open!')
        try:
            with self._conn[self._db].groups.find({},
                    {'_id': False}) as cursor:
                for doc in cursor:
                    yield doc
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def get_readings(self, sensorid, groupid, rtypeid=None,
            limit=DatabaseProvider.DOC_LIMIT):
        """Generator function for retrieving readings from the database.

        Args:
            sensorid (int): The id of the sensor to return readings on.
            groupid (int): The id of the group the sensor belongs to.
            rtypeid (int): The id of the rtype corresponding the reading type to return (default: None).
            limit (int): The number of readings to return in a single call (default: 100).
        """
        if not self._open:
            raise DBError('Cannot get readings, database connection not open!')
        try:
            if rtypeid:
                filters = {"sensorid":sensorid, "groupid":groupid, "rtypeid":rtypeid}
            else:
                filters = {"sensorid":sensorid, "groupid":groupid}
            with self._conn[self._db].readings.find(filters, {"_id":False}).sort("ts", pymongo.DESCENDING).limit(limit) as cursor:
                for doc in cursor:
                    yield doc
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def get_rtypes(self):
        """Generator function used to get reading types from the database.

        Args:
            batch_size (int): The number of reading types to return in each batch.
        """
        if not self._open:
            raise DBError('Cannot get rtypes, database connection not open!')
        try:
            with self._conn[self._db].rtypes.find({}, {'_id': False}) as cursor:
                for doc in cursor:
                    yield doc
        except Exception:
            raise DBError(f'ERROR: {str(e)}')


    async def get_sensors(self, groupid):
        """Generator function used to get sensors from the database.

        Args:
            groupid (int): The id of the group to return sensors from.
            batch_size (int): The number of sensors to return in a single batch.
        """
        if not self._open:
            raise DBError('Cannot get sensors, database connection not open!')
        try:
            groupid = int(groupid)
            with self._conn[self._db].sensors.find({'groupid': groupid}, {'_id': False}) as cursor:
                for doc in cursor:
                    yield doc
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def insert_group(self, groupid, alias):
        """ Inserts a group into the database.

        Args:
            groupid (int): The id of the group.
            alias (str): The human readable alias for the group.
        """
        if not self._open:
            raise DBError('Cannot insert group, database connection not open!')
        groupid = int(groupid)
        try:
            if not await self.does_group_exist(groupid):
                self._conn[self._db].groups.insert_one(
                    {
                        "groupid": groupid,
                        "alias": alias
                    }
                )
        except Exception as e:
            return False, DBError(f'ERROR: {str(e)}')
        return True, None


    async def insert_readings(self, readings, batch_size=DatabaseProvider.BATCH_SIZE):
        """Inserts multiple readings into the database.

        Args:
            readings (list): A list of readings to insert into the database.
            batch_size (int): The amount of readings to insert per batch.
        """
        if not self._open:
            raise DBError('Cannot insert readings, database connection not open!')
        try:
            index = 0
            lim = len(readings)
            while index < lim:
                step = batch_size if index + batch_size < lim else lim - index
                self._conn[self._db].readings.insert_many(readings[index:index+step])
                index += step
        except Exception as e:
            return False, DBError(f'ERROR: {str(e)}')
        return True, None


    async def insert_sensor(self, sensorid, groupid, alias):
        """Inserts a sensorboard into the database.

        Args:
            sensorid (int): The id assigned to the sensorboard.
            groupid (int): The id of the group the sensorboard belongs to.
            alias (str): The alias of the sensor.
        """
        if not self._open:
            raise DBError('Cannot insert sensor, database connection not open!')
        try:
            if not await self.does_sensor_exist(sensorid, groupid):
                self._conn[self._db].sensors.insert_one({
                    'sensorid': sensorid,
                    'groupid': groupid,
                    'alias': alias
                })
        except Exception as e:
            return False, DBError(f'ERROR: {str(e)}')
        return True, None


    def open(self):
        """Opens a connection to the backing database server."""
        if not self._open:
            try:
                if self.__username is not None and self.__password is not None:
                    self._conn = pymongo.MongoClient(
                        self._conn_str,
                        username=self.__username,
                        password=self.__password
                    )
                else:
                    self._conn = pymongo.MongoClient(
                        self._conn_str
                    )
                self._open = True
            except Exception as e:
                raise DBError(f'ERROR: {str(e)}')
        

    async def stats_group(self, groupid, rtypeid, start_ts, end_ts):
        """Returns the stats for an entire group of sensors.

        Args:
            groupid (int): The id of the group the sensor belongs to.
            rtypeid (int): The id of the reading type to retrieve stats for.
            start_ts (datetime.datetime): The start time that begins the range
            for stats.
            end_ts (datetime.datetime): The end time that ends the range for
            stats.

        Returns:
            (generator): A Python generator over the stats from the database.
        """
        # bail if we arent connected to the database
        if not self._open:
            raise DBError('Cannot retrieve stats for sensor, database connection not open!')
        # build the pipeline
        pipeline = [
            # filter all elements that do not match the indicated group and rtype
            {"$match": {
                    "$and": [{
                        "groupid": {"$eq": groupid},
                        "rtypeid": {"$eq": rtypeid}
                    }]
                }
            },
            # optimization step - sort descending by time
            {"$sort":
                {"ts": -1}
            },
            # filter out all elements that do not fit within the time bound
            {"$match": {
                    "$and": [{
                        "ts": {"$gte": start_ts},
                        "ts": {"$lte": end_ts}
                    }]
                }
            }
        ]
        try:
            with self._conn[self._db].readings.aggregate(pipeline,
                    allowDiskUse=True, maxTimeMS=self.MAX_AGGREGATE_MS) as cursor:
                # the above project should only return a single document
                return cursor.next()
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def stats_sensor(self, sensorid, groupid, rtypeid, start_ts, end_ts):
        """Returns the stats for a specific sensor.

        Args:
            sensorid (int): The id of the sensor to retrieve stats on.
            groupid (int): The id of the group the sensor belongs to.
            rtypeid (int): The id of the reading type to retrieve stats for.
            start_ts (int): The start time that begins the range for stats.
            end_ts (int): The end time that ends the range for stats.

        Returns:
            (dict): A Python dict-like object containing the stats for sensor.
        """
        # bail if not connected to the database
        if not self._open:
            raise DBError('Cannot retrieve stats for sensor, database connection not open!')
        # build the stats pipeline
        pipeline = [
            # filter by sensorid, groupid, and rtypeid
            #   these are all indexed so this should be fast
            {"$match": {
                    "$and": [{
                        "sensorid": {"$eq": sensorid},
                        "groupid": {"$eq": groupid},
                        "rtypeid": {"$eq": rtypeid}
                    }]
                }
            },
            # optimization step - sort descending by time
            {"$sort":
                {"ts": -1}
            },
            # filter by time
            {"$match": {
                    "ts": {"$lte": end_ts}
                }
            },
            {"$match": {
                    "ts": {"$gte": start_ts}
                }
            },
            # project just the value field
            {"$project": {"val": 1}},
            # simultaneously determine the min, max, and avg
            # TODO: We may be able to do this entirely in the above
            #   project
            # $facet allows for running simultaneous operations across a
            #   collection without having to run through the collection each
            #   with each operation
            {"$facet": {
                "min": [
                    {"$group":
                        {
                            "_id": None,
                            "value": {"$min": "$val"}
                        }
                    }
                ],
                "max": [
                    {"$group":
                        {
                            "_id": None,
                            "value": {"$max": "$val"}
                        }
                    }
                ],
                "avg": [
                    {"$group":
                        {
                            "_id": None,
                            "value": {"$avg": "$val"}
                        }
                    }
                ]
            }}
        ]
        try:
            # run the aggregation
            doc = None
            with self._conn[self._db].readings.aggregate(pipeline,
                    allowDiskUse=True, maxTimeMS=self.MAX_AGGREGATE_MS) as cursor:
                doc = cursor.next()
            # build the stats container
            stats = dict()
            if doc and doc['min'] and doc['max'] and doc['avg']:
                stats['min'] = doc['min'][0]['value']
                stats['max'] = doc['max'][0]['value']
                stats['avg'] = doc['avg'][0]['value']
            else:
                stats['min'] = 0
                stats['max'] = 0
                stats['avg'] = 0
            # return the stats container
            return stats
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')

    
    async def get_readings_by_period(self, sensorid, groupid, start_ts, end_ts):
        """Returns all of the readings for a given time period for a given
        sensor.

        Args:
            sensorid (int): The id of the sensor to get readings for.
            groupid (int): The id of the group the sensor belongs to.
            start_ts (datetime.datetime): The start time period.
            end_ts (datetime.datetime): The end time period.
        """
        # bail if not connected to the database
        if not self._open:
            raise DBError('Cannot retrieve sensor readings, database connection not open!')
        try:
            pipeline = [
                # filter by sensorid and groupid
                # these are all indexed so this should be fast
                {"$match": {
                        "$and": [{
                            "sensorid": {"$eq": sensorid},
                            "groupid": {"$eq": groupid}
                        }]
                    }
                },
                # optimization step - sort descending by time
                {"$sort":
                    {"ts": -1}
                },
                # filter by time
                {"$match": {
                        "ts": {"$lte": end_ts}
                    }
                },
                {"$match": {
                        "ts": {"$gte": start_ts}
                    }
                },
                {"$project": {
                    "_id": 0, 
                    "groupid": 1, 
                    "sensorid": 1, 
                    "rtypeid": 1, 
                    "ts": 1, 
                    "val": 1}
                }
            ]
            with self._conn[self._db].readings.aggregate(pipeline,
                    allowDiskUse=True, maxTimeMS=self.MAX_AGGREGATE_MS) as cursor:
                for doc in cursor:
                    yield doc
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


class _GenericSQLProvider(DatabaseProvider):
    """Defines a generic SQL database provider. Override the methods
    provided by this class in subclasses as necessary.
    """
    
    def __init__(self, conn_str, db):
        """Returns an instance of a DatabaseProvider. Do not call this function.
        All of the methods defined by the DatabaseProvider class will raise a
        NotImplementedError when called.

        Args:
            conn_str (str): The connection string for the database server.
            db (str): The name of the Senslify database.
        """
        DatabaseProvider.__init__(self, conn_str, db)


    @staticmethod
    @contextmanager
    def get_connection(conn_str, db=None):
        """Gets a connection to the backing database server.

        This method shall be implemented as a generator function, shall yield
        an instance of a DatabaseProvider, and shall close the provider when
        done.

        Args:
            conn_str (str): The connection string to the database server.
            db (str): The name of the Senslify database - unused by this provider.

        Returns:
            DatabaseProvider: A temporary database provider.
        """
        conn = pyodbc.connect(conn_str)
        yield conn
        conn.close()


    async def close(self):
        """Closes the connection to the backing database provider."""
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists. Database connection is not open!')
        try:
            self._conn.close()
            self._is_open = False
        except Exception as e:
            raise DBError(str(e))


    def init(self, migration=True):
        """Initializes the database with the initial table design dictated in
        'Docs/DB.md'.

        This command should either fail soft or prompt the user
        to confirm deletion of the database if the database already exists.

        Arguments:
            migration (boolean): Whether the database is a migration database
            or not (default: True).
        """
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists. Database connection is not open!')
        try:
            with self._conn.cursor() as cursor:
                if not migration:
                    cursor.execute('CREATE TABLE SENSORS (sensorid int, alias varchar(255), PRIMARY KEY(sensorid))')
                    cursor.execute('CREATE TABLE GROUPS (groupid int, alias varchar(255), PRIMARY KEY(groupid))')
                    cursor.execute('CREATE TABLE RTYPES (rtypeid int, alias varchar(255), PRIMARY KEY(rtypeid))')
                cursor.execute('CREATE TABLE READINGS (sensorid int, groupid int, rtypeid int, ts int, value decimal, PRIMARY KEY (sensorid, groupid, rtypeid, ts))')
                if not migration:
                    cursor.execute('ALTER TABLE READINGS ADD FOREIGN KEY (sensorid) REFERENCES SENSORS(sensorid)')
                    cursor.execute('ALTER TABLE READINGS ADD FOREIGN KEY (groupid) REFERENCES GROUPS(groupid)')
                    cursor.execute('ALTER TABLE READINGS ADD FOREIGN KEY (rtypeid) REFERENCES RTYPES(rtypeid)')
        except Exception as e:
            self._conn.rollback()
            raise DBError(str(e))
        finally:
            self._conn.commit()


    async def delete_group(self, groupid):
        """Deletes the indicated group from the database. This operation cascades
        to sensors and readings.

        Args:
            groupid (int): A group identifier.

        Returns:
            (int): The number of records that are deleted.
        """
        if not self._open:
            raise DBError('ERROR: Cannot delete group, database connection is not open!')
        count = 0
        try:
            with self._conn.cursor() as cursor:
                count += cursor.execute('DELETE FROM SENSORS WHERE groupid=?', (groupid))
                count += cursor.execute('DELETE FROM READINGS WHERE groupid=?', (groupid))
                count += cursor.execute('DELETE FROM GROUPS WHERE groupid=?', (groupid))
        except Exception as e:
            self._conn.rollback()
            raise DBError(f'ERROR: {str(e)}')
        finally:
            self._conn.commit()
        return count


    async def delete_reading(self, sensorid, groupid, rtypeid, ts):
        """Deletes the indicated reading from the database.

        Args:
            sensorid (int): A sensor identifier.
            groupid (int): A group identifier.
            rtypeid (int): A reading type identifier.
            ts (int): A UNIX timestamp.

        Returns:
            (int): The number of readings that are deleted.
        """
        if not self._open:
            raise DBError('ERROR: Cannot delete reading from database, database connection is not open!')
        count = 0
        try:
            with self._conn.cursor() as cursor:
                count += cursor.execute('DELETE FROM READINGS WHERE sensorid=? AND groupid=? AND rtypeid=? AND ts=?', (sensorid, groupid, rtypeid, ts))
        except Exception as e:
            self._conn.rollback()
            raise DBError(str(e))
        finally:
            self._conn.commit()
        return count


    async def delete_readings(self, sensorid, groupid, rtypeid=None):
        """Deletes all readings for the indicated sensor. if rtypeid is not
        None, only deletes readings that match the specified reading type.

        Args:
            sensorid (int): A sensor identifier.
            groupid (int): A group identifier.
            rtypeid (int): A reading type identifier (default: None).

        Returns:
            (int): The number of records that are deleted. 
        """
        if not self._open:
            raise DBError('ERROR: Cannot delete readings from database, database connection is not open!')
        count = 0
        try:
            if rtypeid:
                query = 'DELETE FROM READINGS WHERE sensorid=? AND groupid=? AND rtypeid=?'
                params = (sensorid, groupid, rtypeid)
            else:
                query = 'DELETE FROM READINGS WHERE sensorid=? AND groupid=?'
                params = (sensorid, groupid)
            with self._conn.cursor() as cursor:
                count += cursor.execute(query, params)
        except Exception as e:
            self._conn.rollback()
            raise DBError(str(e))
        finally:
            self._conn.commit()
        return count


    async def delete_rtype(self, rtypeid):
        """Deletes the indicated rtype from the database. This operation 
        cascades to readings.

        Args:
            rtypeid (int): A reading type identifier.

        Returns:
            (int): The number of records that are deleted.
        """
        count = 0
        if not self._open:
            raise DBError('ERROR: Cannot delete reading type, database connection is not open!')
        try:
            with self._conn.cursor() as cursor:
                count += cursor.execute('DELETE FROM READINGS WHERE rtypeid=?', (rtypeid))
                count += cursor.execute('DELETE FROM RTYPES WHERE rtypeid=?', (rtypeid))
        except Exception as e:
            self._conn.rollback()
            raise DBError(f'ERROR: {str(e)}')
        finally:
            self._conn.commit()
        return count


    async def delete_sensor(self, groupid, sensorid):
        """Deletes the indicated sensor from the database. This operation
        cascades to readings.

        Args:
            groupid (int): A group identifier.
            sensorid (int): A sensor identifier.

        Returns:
            (int): The number of records that are deleted.
        """
        if not self._open:
            raise DBError('ERROR: Cannot delete sensor, database connection is not open!')
        count = 0
        try:
            with self._conn.cursor() as cursor:
                count += cursor.execute('DELETE FROM READINGS WHERE groupid=? AND sensorid=?', (groupid, sensorid))
                count += cursor.execute('DELETE FROM SENSORS WHERE groupid=? AND sensorid=?', (groupid, sensorid))
        except Exception as e:
            self._conn.rollback()
            raise DBError(f'ERROR: {str(e)}')
        finally:
            self._conn.commit()


    async def does_group_exist(self, groupid):
        """Determines if the specifiied group exists in the database.

        Args:
            groupid (int): The id of the group to check for.

        Returns:
            (boolean): True if the group exists, False otherwise.
        """
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists. Database connection is not open!')
        try:
            with self._conn.cursor() as cursor:
                if not cursor.execute('SELECT * FROM GROUPS WHERE groupid=?', (groupid)).fetchone(): 
                    return False
                return True
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def does_rtype_exist(self, rtypeid):
        """Determines if the specified sensor exists in the database.

        Args:
            rtypeid (int): The id of the rtype to check for.

        Returns:
            (boolean): True if the reading type exists, False otherwise.
        """
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists. Database connection is not open!')
        try:
            with self._conn.cursor() as cursor:
                if not cursor.execute('SELECT * FROM RTYPES WHERE rtypeid=?', (rtypeid)).fetchone():
                    return False
                return True
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def does_sensor_exist(self, sensorid, groupid):
        """Determines if the specified sensor exists in the database.

        Args:
            sensorid (int): The id of the sensor to check for.
            groupid (int): The id of the group the sensor belongs to.

        Returns:
            (boolean): True if the sensor sensor exists, False otherwise.
        """
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists. Database connection is not open!')
        try:
            with self._conn.cursor() as cursor:
                if not cursor.execute('SELECT * FROM SENSORS WHERE groupid=? AND sensorid=?', (groupid, sensorid)).fetchone():
                    return False
                return True
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def find_max_groupid(self):
        '''Determines the maximum groupid stored in the database.'''
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists. Database connection is not open!')
        try:
            with self._conn.cursor() as cursor:
                row = cursor.execute('SELECT MAX(groupid) FROM GROUPS').fetchone()
                if not row: raise DBError
                return row
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def find_max_sensorid_in_group(self, groupid):
        '''Determines the maximum sensor identifier stored in the database for the 
        specified group.

        Arguments:
            groupid (int): A group identifier that the sensor will be provisioned with.
        '''
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists. Database connection is not open!')
        try:
            with self._conn.cursor() as cursor:
                row = cursor.execute('SELECT MAX(sensorid) FROM SENSORS').fetchone()
                if not row: raise DBError
                return row
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def get_groups(self):
        """Generator function used to get groups from the database."""
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists. Database connection is not open!')
        try:
            with self._conn.cursor() as cursor:
                for row in cursor.execute('SELECT * FROM GROUPS').fetchall():
                    yield row
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def get_rtypes(self):
        """Generator function used to get reading types from the database."""
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists. Database connection is not open!')
        try:
            with self._conn.cursor() as cursor:
                for row in cursor.execute('SELECT * FROM RTYPES').fetchall():
                    yield row
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def get_sensors(self, groupid):
        """Generator function used to get sensors from the database.

        Args:
            groupid (int): The id of the group to return sensors from.
        """
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists. Database connection is not open!')
        try:
            with self._conn.cursor() as cursor:
                for row in cursor.execute('SELECT * FROM SENSORS').fetchall():
                    yield row
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def get_readings(self, sensorid, groupid, rtypeid=None, limit=DatabaseProvider.DOC_LIMIT):
        """Generator function for retrieving readings from the database.

        Args:
            sensorid (int): The id of the sensor to return readings on.
            groupid (int): The id of the group the sensor belongs to.
            rtypeid (int): The id of the rtype corresponding the reading type to return (default: None).
            limit (int): The number of readings to return in a single call (default: 100).
        """
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists. Database connection is not open!')
        try:
            if rtype:
                query = 'SELECT * FROM READINGS WHERE sensorid=? AND groupid=? AND rtypeid=? ORDER BY ts DESC'
                params = (sensorid, groupid, rtypeid)
            else:
                query = 'SELECT * FROM READINGS WHERE sensorid=? AND groupid=? ORDER BY ts DESC'
                params = (sensorid, groupid)
            with self._conn.cursor() as cursor:
                for row in cursor.execute(query, params).fetchall():
                    yield row
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def insert_group(self, groupid, alias):
        """Inserts a group into the database.

        Args:
            groupid (int): The id of the group.
            alias (str): The human readable alias for the group.
        """
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists. Database connection is not open!')
        try:
            with self._conn.cursor() as cursor:
                cursor.execute('INSERT INTO GROUPS VALUES (groupid=?, alias=?)', (groupid, alias))
        except Exception as e:
            self._conn.rollback()
            raise DBError(f'ERROR: {str(e)}')
        finally:
            self._conn.commit()


    async def insert_reading(self, reading):
        """Inserts a single reading into the database.

        Args:
            reading (dict): The reading to insert into the database.
        """
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists. Database connection is not open!')
        self.insert_readings([reading])


    async def insert_readings(self, readings, batch_size=DatabaseProvider.BATCH_SIZE):
        """Inserts multiple readings into the database.

        Args:
            readings (list): A list of readings to insert into the database.
            batch_size (int): The amount of readings to insert per batch.
        """
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists. Database connection is not open!')
        try:
            for reading in readings:
                groupid = reading['groupid']
                sensorid = reading['sensorid']
                rtypeid = reading['rtypeid']
                ts = reading['ts']
                val = reading['val']
                with self._conn.cursor() as cursor:
                    cursor.execute('INSERT INTO READINGS VALUES (groupid=?, sensorid=?, rtypeid=?, ts=?, val=?)', (groupid, sensorid, rtypeid, ts, val))
        except Exception as e:
            self._conn.rollback()
            raise DBError(f'ERROR: {str(e)}')
        finally:
            self._conn.commit()


    async def insert_sensor(self, sensorid, groupid, alias):
        """Inserts a sensorboard into the database.

        Args:
            sensorid (int): The id assigned to the sensorboard.
            groupid (int): The id of the group the sensorboard belongs to.
            alias (str): The human readable alias for the sensor.
        """
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists. Database connection is not open!')
        try:
            with self._conn.cursor() as cursor:
                cursor.execute('INSERT INTO SENSORS VALUES (sensorid=?, groupid=?, alias=?)', (sensorid, groupid, alias))
        except Exception as e:
            self._conn.rollback()
            raise DBError(f'ERROR: {str(e)}')
        finally:
            self._conn.commit()


    def open(self):
        """Opens a connection to the backing database server."""
        if not self._open:
            try:
                self._conn = pyodbc.connect(self._conn_str)
                self._open = True
            except Exception as e:
                raise DBError(f'ERROR: {str(e)}')


    async def stats_group(self, groupid, rtypeid, start_ts=None, end_ts=None):
        """Returns the stats for an entire group of sensors.

        Args:
            groupid (int): The id of the group the sensor belongs to.
            rtypeid (int): The id of the reading type to retrieve stats for.
            start_ts (datetime.datetime): The start time that begins the range
            for stats (default:None).
            end_ts (datetime.datetime): The end time that ends the range for
            stats (default: None).

        Returns:
            (generator): A Python generator over the stats from the database.

        Raises:
            (Exception): If there was a problem interacting with the database.
        """
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists. Database connection is not open!')
        try:
            with self._conn.cursor() as cursor:
                for row in cursor.execute('SELECT AVG(val), MAX(val), MIN(val), sensorid, groupid FROM READINGS WHERE groupid=? AND rtypeid=? AND ts>=? and ts<? GROUPBY sensorid, groupid', (groupid, rtypeid, start_ts, end_ts)).fetchall():
                    yield row
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def stats_sensor(self, sensorid, groupid, rtypeid, start_ts, end_ts):
        """Returns the stats for a specific sensor.

        Args:
            sensorid (int): The id of the sensor to retrieve stats on.
            groupid (int): The id of the group the sensor belongs to.
            rtypeid (int): The id of the reading type to retrieve stats for.
            start_date (datetime.datetime): The start time that begins the range
            for stats.
            end_date (datetime.datetime): The end time that ends the range for
            stats.

        Raises:
            (Exception): If there was a problem interacting with the database.
        """
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists. Database connection is not open!')
        try:
            with self._conn.cursor() as cursor:
                return cursor.execute('SELECT AVG(val), MAX(val), MIN(val) WHERE sensorid=? AND groupid=? AND rtypeid=? AND ts>=? AND ts<?', (sensorid, groupid, rtypeid, ts)).fetchone()
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


    async def get_readings_by_period(self, sensorid, groupid, start_ts, end_ts):
        """Returns all of the readings for a given time period for a given
        sensor.

        Args:
            sensorid (int): The id of the sensor to get readings for.
            groupid (int): The id of the group the sensor belongs to.
            start_ts (datetime.datetime): The start time period.
            end_ts (datetime.datetime): The end time period.
        """
        if not self._open:
            raise DBError('ERROR: Cannot determine if group exists. Database connection is not open!')
        try:
            with self._conn.cursor() as cursor:
                for row in cursor.execute().fetchall('SELECT * FROM READINGS WHERE sensorid=? AND groupid=? AND ts >= ? AND ts < ? ORDER BY ts DESC', (sensorid, groupid, start_ts, end_ts)):
                    yield row
        except Exception as e:
            raise DBError(f'ERROR: {str(e)}')


class PostGresProvider(_GenericSQLProvider):
    """Defines a provider for a PostGres SQL server instance.
    """

    def __init__(self, conn_str, db):
        """Returns an instance of a DatabaseProvider. Do not call this function.
        All of the methods defined by the DatabaseProvider class will raise a
        NotImplementedError when called.

        Args:
            conn_str (str): The connection string for the database server.
            db (str): The name of the Senslify database.
        """
        _GenericSQLProvider.__init__(self, conn_str, db)


    def open(self):
        """Opens a connection to the backing database server."""
        if not self._open:
            try:
                self._conn = pyodbc.connect(self._conn_str)
                # PGSQL supports single encoding for all text data by default - manually specify utf-8 for 
                #   Python compatibility
                self._conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
                self._conn.setencoding(encoding='utf-8')
                # PGSQL odbc driver only supports 255-byte max varchar/wvarcharsize severely limiting
                #   write performance - this fixes the issue
                self._conn.maxwrite = 1024 * 1024 * 1024
                self._open = True
            except Exception as e:
                raise DBError(f'ERROR: {str(e)}')


class SQLServerProvider(_GenericSQLProvider):
    """Defines a provider for a MS SQL Server instance."""

    def __init__(self, conn_str, db):
        """Returns an instance of a DatabaseProvider. Do not call this function.
        All of the methods defined by the DatabaseProvider class will raise a
        NotImplementedError when called.

        Args:
            conn_str (str): The connection string for the database server.
            db (str): The name of the Senslify database.
        """
        _GenericSQLProvider.__init__(self, conn_str, db)