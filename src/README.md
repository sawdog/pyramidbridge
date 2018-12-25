* Event messaging bridge for SmartThings Connectors

Currently messages from the /smartthings/v1/events/put go directly to rethinkDB.
Thecurrent design plan is to implement support for routing keys within the
event payload. The route(s) are to be configurable from within the SmartThings
mobile application and support pluggable endpoints, for example for the
following backends:

1.  rethinkDB
2.  InfluxDB
3.  RabbitMQ (MQTT)

Ultimately it will be a generic bridge for configurable message delivery and
routing from within SmartThings.

** Project

The project uses a selective core components to build ontop of, ensuring that
extensibility is easy and using existing tools to fit the bill. The project can
easily run as is, without any additional modifications or it can easily be
extended, integrating additional functionality or co-existing with our platform
as it exists today. It can be easily extended to support custom requirements
such as Authentication. The choice for relying on a core component is that each
has it's own ecosystem, developer documenation, but most imporantly it allows
users easily modifcation and extensibility of this project. If users have
additional use cases, please consider integrating those with the core project if
it is a general use case come chat with us or create pull-request. If it is not
a general use case, that's cool too.

*** Pyramid
[Documentation](https://docs.pylonsproject.org/projects/pyramid/en/latest/)

Pyramid is a small, fast, down-to-earth Python web framework. Pyramid utilizes
HTTP/S to expose the bridging functionality as a service. Pyramid is is very
extensible and easily configured, allowing users to add additional functionality
or integrate existing projects onto the framework with very little effort.

**** Support

Pyramid has extensive documentation, a mailing list and an active IRC pressence
on freenode #pyramid

*** Webpack
[Documentation](https://webpack.js.org/)

Webpack is a node.js project utilized to manage the static assets of this
project.  See the webpack documentation on how to utilize and extend the assets
of this project to be styled or support your needs.

**** Support

See the online documentation.



** Project Support

*** Documentation

Currently the project documentation is found in the git repository. It is at 
[github prokject](https://github.com/sawdog/pyramidbridge) and mirrored on
[GitLabs](https://gitlab.com/sawdog/pyramidbridge)

*** Chat

Active developers of this project are generally on IRC @freenode #pyramid
You can also find them in our Slack channel @ opesse.slack.com

