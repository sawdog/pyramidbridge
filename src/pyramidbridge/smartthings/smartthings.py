import pyramid.httpexceptions as exc
from pyramid.response import Response
from pyramid.view import view_config

import rethinkdb as r

from pyramidbridge.rethinkdb.adapter import rethinkDBAdapter
from pyramidbridge.utils import setup_logger
from pyramidbridge.views import BaseView
from pyramidbridge.yamlcfg import yamlcfg

logger = setup_logger()

HOST = yamlcfg.rethinkdb.host
PORT = yamlcfg.rethinkdb.port
USER = yamlcfg.rethinkdb.user
PASSWORD = yamlcfg.rethinkdb.password
DB = yamlcfg.rethinkdb.smartthings.db
EVENTS_TABLE = yamlcfg.rethinkdb.smartthings.events.table
SUBSCRIBE_TABLE = yamlcfg.rethinkdb.smartthings.subscribe.table


class API(BaseView):
    """View Class to handle rendering smartthings views"""

    __adapter__ = None

    def __init__(self, request):
        super(API, self).__init__(request)
        self.__adapter__ = rethinkDBAdapter(table=EVENTS_TABLE)
        import pdb; pdb.set_trace()
        self.page_title = 'SmartThings'



    @property
    def adapter(self):
        return self.__adapter__

    @property
    def connection(self):
        return self.__adapter__.connection

    @view_config(route_name='api.smartthings.v1.events.add',
                 renderer="json",
                 request_method="POST")
    def event_add(self):
        """Add an event API method"""
        try:
            event = self.request.json_body
            logger.debug(event)
        except AttributeError:
            return exc.HTTPBadRequest()

        # todo: lookup routes; have interface for ea. route connector
        event.update(dict(created=r.now(),
                          table=EVENTS_TABLE))
        status = self.adapter.add(event)
        return Response(
                status='202 Accepted',
                content_type='application/json; charset=UTF-8')

    @view_config(route_name='api.smartthings.v1.events.list',
                 renderer="json",
                 request_method="GET")
    def events_list(self):
        """
        todo register adapters - and return events
        :return:
        """
        import pdb; pdb.set_trace()
        logger.debug('Listing Events')
        items = self.adapter.items()
        return items

    @view_config(route_name='api.smartthings.v1.subscribe',
                 renderer="json",
                 request_method="POST")
    def post_subscribe(self):
        """API for smartthings to post the subscriber list for the bridge

           This is for looking up to send notifications back to SmartThings
           if it is listening for updates.

        """
        try:
            event = self.request.json_body
        except AttributeError:
            return exc.HTTPBadRequest()

        logger.debug(event)
        r = self.connection.r
        event.update(dict(created=r.now()))
        query = r.table(SUBSCRIBE_TABLE)
        query.insert(event).run(connection.session)
        return Response(
                status='202 Accepted',
                content_type='application/json; charset=UTF-8')


class Integration(BaseView):
    """View to manage the integration


    """
    database = 'smartthings'

    def __init__(self, request):
        super(Integration, self).__init__(request)


    def tables(self):
        pass

