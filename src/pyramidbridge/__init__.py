from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    #config.register
    config.include('pyramid_services')
    config.include('pyramid_chameleon')
    #configure_zpt_renderer(["pyramidbridge:widgets/templates"])
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('api.index', '/api/v1/')
    config.add_route('api.smartthings.v1.events.list', '/api/v1/smartthings/events')
    config.add_route('api.smartthings.v1.events.add', '/api/v1/smartthings/events')
    config.add_route('api.smartthings.v1.subscribe', '/api/v1/smartthings/subscribe')
    config.add_route('home', '/')
    config.add_route('integrations.rethinkdb', '/integrations/rethinkdb')
    config.add_route('integrations.smartthings', '/integrations/smartthings')
    config.add_route('logout', '/logout')
    config.scan()
    return config.make_wsgi_app()
