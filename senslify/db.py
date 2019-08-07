# make pymongo work with async code
import gevent
gevent.monkey.patch_all()

import pymongo


def create_pymongo(app):
    '''
    Defines a method for safely initializing the database connection.
    Arguments:
        app: The web application utilizing the database connection.
    '''
    app['db'] = pymongo.MongoClient(app['config'].mongo_url)


def dispose_pymongo(app):
    '''
    Defines a method for safely closing the database connection.
    Arguments:
        app: The web application utilizing the database connection.
    '''
    app['db'].close()
    
    
def does_sensor_exist(db, sensor, group):
    try:
        return db.senslify.sensors.find_one({'sensor': sensor, 'group': group}) is not None
    except pymongo.errors.ConnectionFailure as e:
        raise e
    except pymongo.errors.PyMongoError as e:
        raise e
        
        
def does_group_exist(db, group):
    try:
        return db.senslify.groups.find_one({'group': group}) is not None
    except pymongo.errors.ConnectionFailure as e:
        raise e
    except pymongo.errors.PyMongoError as e:
        raise e


def get_groups(db):
    groups = []
    try:
        with db.senslify.groups.find() as cursor:
            for group in cursor:
                groups.append(group)
    except pymongo.errors.ConnectionFailure as e:
        raise e
    except pymongo.errors.PyMongoError as e:
        raise e
    return groups
    
    
def get_rtypes(db):
    rtypes = []
    try:
        with db.senslify.groups.find() as cursor:
            for rtype in cursor:
                rtypes.append(rtype)
    except pymongo.errors.ConnectionFailure as e:
        raise e
    except pymongo.errors.PyMongoError as e:
        raise e
    return rtypes


def get_sensors(db, group):
    sensors = []
    try:
        with db.senslify.groups.find('group': group) as cursor:
            for sensor in cursor:
                sensors.append(sensor)
    except pymongo.errors.ConnectionFailure as e:
        raise e
    except pymongo.errors.PyMongoError as e:
        raise e
    return sensors


def get_readings(db, sensor, group, limit=100):
    readings = []
    try:
        # TODO: Only want to select the most recent readings
        with db.senslify.groups.find({'sensor': sensor, 'group': group}).limit(100) as cursor:
            for reading in cursor:
                readings.append(reading)
    except pymongo.errors.ConnectionFailure as e:
        raise e
    except pymongo.errors.PyMongoError as e:
        raise e
    return readings
    
    
def insert_reading(db, reading):
    # only insert if the reading contains a sensor and group
    if 'sensor' not in reading or 'group' not in reading:
        return
    # make sure that the sensor and group already exist
    
