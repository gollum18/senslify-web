import aiomongo


async def create_aiomongo(app):
    '''
    Defines a method for safely initializing the database connection.
    Arguments:
        app: The web application utilizing the database connection.
    '''
    app['db'] = await aiomongo.create_client(app['config'].mongo_url)


async def dispose_aiomongo(app):
    '''
    Defines a method for safely closing the database connection.
    Arguments:
        app: THe web application utilizing the database connection.
    '''
    app['db'].close()
    await app['db'].wait_closed()
