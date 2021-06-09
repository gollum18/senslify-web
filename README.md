# Senslify
Welcome to Senslify. Senslify is a web visualization tool for dislaying archived and live sensor data in real-time. Senslify makes extensive use of asynchronous programming as well as modern advancements in web streaming to provide a modern approach to sensor visualization.


## A Note on Security
The database for Senslify is intentionally unsecured as Senslify is a front-end
for a research project. If and when I decide to release Senslify in the wild,
I will implement security on the database side of the application. However, 
as what is currently a private use project, I (as well as others in the 
project) do not want to introduce additional complexity in running the 
software. If you fork the software and want to use it yourself, then I implore
you to implement some sort of database security before deploying the
software, otherwise, you'll be in for some difficulties in the near future.


## Dependencies
Senslifies server is written in pure Python3 and has the following dependencies.
+ [aiodns](https://pypi.org/project/aiodns/)
+ [aiohttp](https://pypi.org/project/aiohttp/)
+ [aiohttp-jinja2](https://pypi.org/project/aiohttp-jinja2/)
+ [cchardet](https://pypi.org/project/cchardet/)
+ [gevent](https://pypi.org/project/gevent/)
+ [pymongo](https://pypi.org/project/pymongo/)
+ [sphinx](https://pypi.org/project/Sphinx/)


`aiohttp-jinja2` is an extension to the `aiohttp` asynchronous web framework that provides jinja2 templating to aiohttp (jinja2 can best be seen in frameworks like Flask).


`aiodns` and `cchardet` are technically optional dependencies. They are not required to run the server, but provide additional support that increase the servers efficiency. As such, they are recommended.


I employ `gevent` primarily as a means to make the `pymongo` MongoDB
connector async compatible. PyMongo is generally already async compatible
but an overlay has to be constructed on top of the driver to make it work.
I had considered using a library like Motor or aiomongo, but for reasons
documented elsewhere in this project, I have decided to stick with PyMongo.


In addition to the above Python3 requirements, Senslify automatically pulls in the following Javascript and CSS libraries client side:
+ [Bootstrap](https://getbootstrap.com/)
+ [Chart.js](https://www.chartjs.org/)
+ [JQuery](https://jquery.com/)
+ [Popper](https://popper.js.org/)


Bootstrap provides the theming functionality for the web application (although
its not currently themed as of yet).


Chart.js is a free graphing/charting client side Javascript library for displaying datapoints in real-time. I considered several alternatives before
coming across Chart.js but most were paid/non open-source, while Chart.js
was an antithesis to both. Plus it nicely handles automatic resizing, and animation. It also integrates well with bootstrap. Sensor data is displayed
in real-time using WebSockets - [RFC 6455](https://tools.ietf.org/html/rfc6455), [Mozilla API](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API).


Finally Senslify relies on the following external programs:
+ [MongoDB](https://www.mongodb.com/)


While Senslify is setup to use MongoDB, it does not have to. I have recently
generisized the database interface so users of this software should just be 
able to implement their own database interface on top of a connector of their
choice, as long as the connector is async compatible.


## Documentation
Much of the documentation for this project is auto-generated via Sphinx.
However, there are certain documents (found in the 'Root/Docs' folder) that 
contain additional information regarding the Senslify project such as a
formal description of the structure of the database.
