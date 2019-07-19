# Senslify
Welcome to Senslify. Senslify is a web visualization tool for dislaying archived and live sensor data in real-time. Senslify makes extensive use of asynchronous programming as well as modern advancements in web streaming to provide a modern approach to sensor visualization.

# Dependencies
Senslifes server is written in pure Python3 and has the following dependencies.
+ [aiodns]()
+ [aiohttp]()
+ [aiohttp-jinja2]()
+ [aiohttp-sse]()
+ [aiomongo]()
+ [cchardet]()


`aiohttp-jinja2` and `aiohttp-sse` are extensions to the `aiohttp` asynchronous web framework that respectively provide jinja2 templating and server-side events support to `aiohttp`. Server side events provide the live charting functionality of Senslify.


`aiodns` and `cchardet` are technically optional dependencies. They are not required to run the server, but provide additional support that increase the servers efficiency. As such, they are recommended.


`aiomongo` is an asyncio port of the official PyMongo MongoDB Python driver. Its authors claim that it passes all of the same tests that the PyMongo driver does, but it is not mature and is still developing software. That said, this project makes no use of PyMongo's more advanced features aside from basic CRUD operations, so as long as the `aiomongo` package does not terribly break, it should be fine to use.


In addition to the above Python3 requirements, Senslify automatically pulls in the following Javascript and CSS libraries client side:
+ [Bootstrap]()
+ [Chart.js]()
+ [JQuery]()
+ [Popper]()


Bootstrap provides the theming functionality for 


There was a good deal of time spent trying to find a charting library that allowed dynamic resizing and animation functionality all in the same package while still mainintaing true open-source status. Chart.js meets all of the requirements needed for this project, and is completely free to use.


Finally Senslify relies on the following external programs:
+ [MongoDB]()
