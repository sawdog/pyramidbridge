import pyramid.httpexceptions as exc
from pyramid.response import Response
from pyramid.view import view_config

from . import utils
from .connection import Connection
from .yamlcfg import yamlcfg

logger = utils.setup_logger()

HOST = yamlcfg.rethinkdb.host
PORT = yamlcfg.rethinkdb.port
USER = yamlcfg.rethinkdb.user
PASSWORD = yamlcfg.rethinkdb.password
DB = yamlcfg.rethinkdb.smartthings.db
EVENTS_TABLE = yamlcfg.rethinkdb.smartthings.events.table
SUBSCRIBE_TABLE = yamlcfg.rethinkdb.smartthings.subscribe.table


@view_config(route_name='smartthings_add_event', renderer="json", request_method="POST")
def add_event(request):
    # move to a smartthings class
    try:
        event = request.json_body
        #logger.debug(event)
    except AttributeError:
        return exc.HTTPBadRequest()

    connection = Connection(HOST, PORT, USER, PASSWORD, DB)
    r = connection.r
    event.update(dict(created=r.now()))
    query = r.table(EVENTS_TABLE)
    query.insert(event).run(connection.session)
    return Response(
            status='202 Accepted',
            content_type='application/json; charset=UTF-8')


@view_config(route_name='smartthings_subscribe', renderer="json", request_method="POST")
def subscribe(request):
    # move to a smartthings class
    try:
        event = request.json_body
    except AttributeError:
        return exc.HTTPBadRequest()

    #logger.debug(event)
    connection = Connection(HOST, PORT, USER, PASSWORD, DB)
    r = connection.r
    event.update(dict(created=r.now()))
    query = r.table(SUBSCRIBE_TABLE)
    query.insert(event).run(connection.session)
    return Response(
            status='202 Accepted',
            content_type='application/json; charset=UTF-8')

