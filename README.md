# Pyramid bridge

Pyramid bridge is for the SmartThings IoT hub, with the design intention to support pluggable routing endpoints. These routing endpoints are know handlers for given endpoints that require formatting or some kind of handler after SmartThings POSTs the data payload. 

## SmartThings Connector

Within the context of new SmartThings development, this proect will be playing the role of a **SmartThings Connector**. This bridge is currently supporting a single backend, with the plan to support several additional pluggable routes as well as support for a rabbitMQ route, which will in-turn support multiple routes if the SmartThings client is configured as such: a single event is placed into several routes, where ea. has an explicit handler, so that events can be managed across a wide variety of backends.

### SmartThings Developers

See [SmartThiings Developers](https://smartthings.developer.samsung.com/develop/index.html) for more details on the SmartThings developer platform.
