# THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
# APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
# HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT
# WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
# PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE
# DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR
# CORRECTION.

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


import bson, pymongo, sys
from contextlib import contextmanager
from senslify.errors import DBError
from senslify.verify import verify_reading


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


    def init(self):
        """Initializes the database with the initial table design dictated in
        'Docs/DB.md'.

        This command should either fail soft or prompt the user
        to confirm deletion of the database if the database already exists.
        """
        raise NotImplementedError


    async def does_group_exist(self, groupid):
        """Determines if the specifiied group exists in the database.

        Args:
            groupid (int): The id of the group to check for.
        """
        raise NotImplementedError


    async def does_rtype_exist(self, rtypeid):
        """Determines if the specified sensor exists in the database.

        Args:
            rtypeid (int): The id of the rtype to check for.
        """
        raise NotImplementedError


    async def does_sensor_exist(self, sensorid, groupid):
        """Determines if the specified sensor exists in the database.

        Args:
            sensorid (int): The id of the sensor to check for.
            groupid (int): The id of the group the sensor belongs to.
        """
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


    async def get_readings(self, sensorid, groupid, limit=DOC_LIMIT):
        """Generator function for retrieving readings from the database.

        Args:
            sensorid (int): The id of the sensor to return readings on.
            groupid (int): The id of the group the sensor belongs to.
            limit (int): The number of readings to return in a single call.
        """
        raise NotImplementedError


    async def insert_group(self, groupid):
        """Inserts a group into the database.

        Args:
            groupid (int): The id of the group.
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


    async def insert_sensor(self, sensorid, groupid):
        """Inserts a sensorboard into the database.

        Args:
            sensorid (int): The id assigned to the sensorboard.
            groupid (int): The id of the group the sensorboard belongs to.
        """
        raise NotImplementedError


    def is_open(self):
        return self._open


    def open(self):
        """Opens a connection to the backing database server."""
        raise NotImplementedError


    async def stats_group(self, groupid, rtypeid, start=None, end=None):
        """Returns the stats for an entire group of sensors.

        Args:
            groupid (int): The id of the group the sensor belongs to.
            rtypeid (int): The id of the reading type to retrieve stats for.
            start (datetime.datetime): The start time that begins the range
            for stats (default:None).
            end (datetime.datetime): The end time that ends the range for
            stats (default: None).

        Returns:
            (generator): A Python generator over the stats from the database.

        Raises:
            (Exception): If there was a problem interacting with the database.
        """
        raise NotImplementedError


    async def stats_sensor(self, sensorid, groupid, rtypeid, start, end):
        """Returns the stats for a specific sensor.

        Args:
            sensorid (int): The id of the sensor to retrieve stats on.
            groupid (int): The id of the group the sensor belongs to.
            rtypeid (int): The id of the reading type to retrieve stats for.
            start (datetime, datetime): The start time that begins the range
            for stats.
            end (datetime.datetime): The end time that ends the range for
            stats.

        Raises:
            (Exception): If there was a problem interacting with the database.
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


    def init(self):
        """Initializes the database with the initial table design dictated in
        'docs/DB.rst'. This command will fail-soft if the database already
        exists.
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
        except pymongo.errors.PyMongoError as e:
            print(e)
            raise DBError()
        except Exception:
            raise DBError()


    async def does_group_exist(self, groupid):
        """Determines if the specifiied group exists in the database.

        Args:
            groupid (int): The id of the group to check for.
        """
        if not self._open:
            print('Cannot determine if group exists, database connection not open!')
            return
        try:
            return self._conn[self._db].groups.find_one(
                filter={'groupid': groupid}) is not None
        except pymongo.errors.PyMongoError:
            raise DBError()
        except Exception:
            raise DBError()


    async def does_rtype_exist(self, rtypeid):
        """Determines if the specified sensor exists in the database.

        Args:
            rtypeid (int): The id of the rtype to check for.
        """
        if not self._open:
            print('Cannot determine if rtype exists, database connection not open!')
            return
        try:
            return self._conn[self._db].rtypes.find_one(
                filter={'rtypeid': rtypeid}) is not None
        except pymongo.errors.PyMongoError:
            raise DBError()
        except Exception as e:
            raise DBError()


    async def does_sensor_exist(self, sensorid, groupid):
        """Determines if the specified sensor exists in the database.

        Args:
            sensorid (int): The id of the sensor to check for.
        """
        if not self._open:
            print('Cannot determine if sensor exists, database connection not open!')
            return
        try:
            return self._conn[self._db].sensors.find_one(
                    filter={'sensorid': sensorid,
                            'groupid': groupid}) is not None
        except pymongo.errors.PyMongoError:
            raise DBError()
        except Exception:
            raise DBError()


    async def get_groups(self):
        """Generator function used to get groups from the database.

        Args:
            batch_size (int): The number of groups to return in each batch.
        """
        if not self._open:
            print('Cannot get groups, database connection not open!')
            return
        try:
            with self._conn[self._db].groups.find({},
                    {'_id': False}) as cursor:
                for doc in cursor:
                    yield doc
        except pymongo.errors.PyMongoError:
            raise DBError()
        except Exception:
            raise DBError()


    async def get_readings(self, sensorid, groupid, rtypeid,
            limit=DatabaseProvider.DOC_LIMIT):
        """Generator function for retrieving readings from the database.

        Args:
            sensorid (int): The id of the sensor to return readings on.
            groupid (int): The id of the group the sensor belongs to.
            limit (int): The number of readings to return in a single call.
        """
        if not self._open:
            print('Cannot get readings, database connection not open!')
            return
        try:
            sensorid = int(sensorid)
            groupid = int(groupid)
            rtypeid = int(rtypeid)
            with self._conn[self._db].readings.find({"sensorid":sensorid, "groupid":groupid, "rtypeid":rtypeid}, {"_id":False}).sort("ts", pymongo.DESCENDING).limit(limit) as cursor:
                for doc in cursor:
                    yield doc
        except pymongo.errors.PyMongoError:
            raise DBError()
        except Exception:
            raise DBError()


    async def get_rtypes(self):
        """Generator function used to get reading types from the database.

        Args:
            batch_size (int): The number of reading types to return in each batch.
        """
        if not self._open:
            print('Cannot get rtypes, database connection not open!')
            return
        try:
            with self._conn[self._db].rtypes.find({}, {'_id': False}) as cursor:
                for doc in cursor:
                    yield doc
        except pymongo.errors.PyMongoError:
            raise DBError()
        except Exception:
            raise DBError()


    async def get_sensors(self, groupid):
        """Generator function used to get sensors from the database.

        Args:
            groupid (int): The id of the group to return sensors from.
            batch_size (int): The number of sensors to return in a single batch.
        """
        if not self._open:
            print('Cannot get sensors, database connection not open!')
            return
        try:
            groupid = int(groupid)
            with self._conn[self._db].sensors.find({'groupid': groupid}, {'_id': False}) as cursor:
                for doc in cursor:
                    yield doc
        except pymongo.errors.PyMongoError:
            raise DBError()
        except Exception:
            raise DBError()


    async def insert_group(self, groupid):
        """ Inserts a group into the database.

        Args:
            groupid (int): The id of the group.
        """
        if not self._open:
            print('Cannot insert group, database connection not open!')
            return
        groupid = int(groupid)
        try:
            if not await self.does_group_exist(groupid):
                self._conn[self._db].groups.insert_one({"groupid": groupid})
        except pymongo.errors.PyMongoError:
            raise DBError()
        except Exception:
            raise DBError()


    async def insert_reading(self, reading):
        """Inserts a single reading into the database.

        Args:
            reading (dict): The reading to insert into the database.
        """
        if not self._open:
            print('Cannot insert reading, database connection not open!')
            return
        # FIX: The verify operation is now performed in the upload handler
        try:
            # remove the command if necessary
            if "cmd" in reading:
                del reading['cmd']
            sensorid = int(reading['sensorid'])
            groupid = int(reading['groupid'])
            rtypeid = int(reading['rtypeid'])
            # insert the sensor if it does not exist
            if not await self.does_sensor_exist(sensorid, groupid):
                await self.insert_sensor(sensorid, groupid)
            if not await self.does_group_exist(groupid):
                await self.insert_group(groupid)
            # make sure that the rtype exists, exit otherwise
            if not await self.does_rtype_exist(rtypeid):
                print('rtype:', rtypeid, 'not found in database!')
                return
            # insert the reading into the database
            self._conn[self._db].readings.insert_one(reading)
        except pymongo.errors.PyMongoError:
            return False, DBError()
        except Exception:
            return False, DBError()
        return True, None


    async def insert_readings(self, readings, batch_size=DatabaseProvider.BATCH_SIZE):
        """Inserts multiple readings into the database.

        Args:
            readings (list): A list of readings to insert into the database.
            batch_size (int): The amount of readings to insert per batch.
        """
        if not self._open:
            print('Cannot insert readings, database connection not open!')
            return
        if not map(verify_reading, readings):
            return False, None
        try:
            index = 0
            lim = len(readings)
            while index < lim:
                step = batch_size if index + batch_size < lim else lim - index
                self._conn[self._db].readings.insert_many(readings[index:index+step])
                index += step
        except pymongo.errors.PyMongoError:
            return False, DBError()
        except Exception:
            return False, DBError()
        return True, None


    async def insert_sensor(self, sensorid, groupid):
        """Inserts a sensorboard into the database.

        Args:
            sensorid (int): The id assigned to the sensorboard.
            groupid (int): The id of the group the sensorboard belongs to.
        """
        if not self._open:
            print('Cannot insert sensor, database connection not open!')
            return
        try:
            self._conn[self._db].sensors.insert_one({
                'sensorid': sensorid,
                'groupid': groupid
            })
        except pymongo.errors.PyMongoError:
            return False, DBError()
        except Exception:
            return False, DBError()
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
            except pymongo.errors.PyMongoError:
                print('ERROR: Cannot continue, there was a problem opening the database connection!\n{}'.format(str(e)))
                raise DBError()


    async def stats_group(self, groupid, rtypeid, start, end):
        """Returns the stats for an entire group of sensors.

        Args:
            groupid (int): The id of the group the sensor belongs to.
            rtypeid (int): The id of the reading type to retrieve stats for.
            start (datetime.datetime): The start time that begins the range
            for stats.
            end (datetime.datetime): The end time that ends the range for
            stats.

        Returns:
            (generator): A Python generator over the stats from the database.
        """
        # bail if we arent connected to the database
        if not self._open():
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
                        "ts": {"$gte": start},
                        "ts": {"$lte": end}
                    }]
                }
            }
        ]
        try:
            with self._conn[self._db].readings.aggregate(pipeline,
                    allowDiskUse=True, maxTimeMS=self.MAX_AGGREGATE_MS) as cursor:
                return cursor.next()
        except Exception:
            raise DBError()


    async def stats_sensor(self, sensorid, groupid, rtypeid, start, end):
        """Returns the stats for a specific sensor.

        Args:
            sensorid (int): The id of the sensor to retrieve stats on.
            groupid (int): The id of the group the sensor belongs to.
            rtypeid (int): The id of the reading type to retrieve stats for.
            start (datetime, datetime): The start time that begins the range
            for stats.
            end (datetime.datetime): The end time that ends the range for
            stats.

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
                    "ts": {"$lte": end}
                }
            },
            {"$match": {
                    "ts": {"$gte": start}
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
        except Exception:
            raise DBError()
