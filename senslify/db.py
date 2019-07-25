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
