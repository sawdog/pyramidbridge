"""base layout View class"""
import copy
#from deform import Form

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.security import (
    authenticated_userid,
    forget,
)
from pyramid.view import (
    forbidden_view_config,
    view_config,
)

BREADCRUMB_LI = '<li class="breadcrumb-item%(active)s %(section)s">%(li)s</li>'
BREADCRUMB_HREF = '<a href="%(href)s" id="%(bchrefid)s">%(text)s</a>'


class API(object):
    """Simple view for API views to derive from; excludes any view related
       setup and logic.

    """

    def __init__(self, request):
        self.request = request


class BaseView(object):

    __action__ = ''
    _active_route_ = None
    _crumb_title_ = None
    _include_breadcrumbs_ = False
    _include_leftnav_ = True
    _leftnav_urls_ = None
    _listing_view_order_by = 'uid'
    header_icon = None
    section = 'light'
    section_content_header_css = 'primary-static'

    def __init__(self, request):
        self._error = False
        self.request = request
        self.buttons = ('submit',)

    def _admin(self):
        """
           XXX hack for assigning admin hook for template to permission
           specific items.  Need to re-model the nav/actions so they can
           do a permission check directly.

        """
        return self.request._admin

    def _manage_patients(self):
        """Stuffed on the request during group lookup....
           XXX baby kittens scream
        """
        return self.request._manage_patients

    def _assign_programs(self):
        """Stuffed on the request during group lookup....
           XXX baby kittens scream
        """
        return self.request._assign_programs

    def _get_filtered_listing_items(self):
        raise NotImplementedError

    def _get_listing_items(self):
        return self.request.db.query(self.__model__).filter(
                self.__model__.uid > 0).order_by(self._listing_view_order_by)

    def _content_navigation(self, context=None, **kw):
        nav = {}
        active = kw.get('active')
        if context is None and kw.get('context') is None:
            context = self.request.user

        if active is None:
            active = self._active_route_

        if self._include_leftnav_:
            leftnav = self.leftnav(context,
                                   active=active,
                                   urls=kw.get('leftnav_urls'))
            nav['leftnavitems'] = leftnav

        if self._include_breadcrumbs_:
            breadcrumbs = self.breadcrumbs(context,
                                           active=active,
                                           urls=kw.get('crumbs'))
            nav['breadcrumbs'] = breadcrumbs

        return nav

    def _leftnav_urls(self):
        """ Override and build the left nav structure for the view"""
        urls = copy.deepcopy(self._leftnav_urls_)
        return urls

    def active_route_leftnav(self, remove=False):
        leftnav_urls = copy.deepcopy(self._leftnav_urls_)
        if remove:
            try:
                del leftnav_urls[self._active_route_]
            except KeyError:
                pass

        return leftnav_urls

    def breadcrumbs(self, obj, active=None, urls=None):
        """ build the breadcrumb structure """
        request = self.request
        if urls is None:
            urls = copy.deepcopy(self._breadcrumbs_)

        if active is None:
            active = self._active_route_

        for k, v in urls.items():
            if k == active or k is None:
                aval = 'active'
            else:
                aval = ''

            attrs = v[1].split(',')
            litext = v[2]
            if len(attrs) == 2:
                uid = attrs[0]
                kw = {uid: getattr(obj, attrs[1])}
            elif len(attrs) == 3:
                uid = attrs[0]
                kw = {uid: getattr(obj, attrs[1])}
                # passing in item 2 from the tuple as:
                # 'uid,func_or_attr,optional:val' --
                # if need arises, can iterate past index 1
                kw.update(dict([attrs[2].split('=')]))
            else:
                kw = dict(uid=getattr(obj, attrs[0]))

            if aval == 'active':
                url = (v[0], BREADCRUMB_LI % {'active': ' ' + aval,
                                              'section': ' ' + self.section,
                                              'li': litext})
            else:
                href = BREADCRUMB_HREF % {'href': request.route_url(k, **kw),
                                          'bchrefid': v[3],
                                          'text': litext}
                url = (v[0], BREADCRUMB_LI % {'active': aval,
                                              'section': self.section,
                                              'li': href})
            urls[k] = url

        crumbs = urls.values()
        crumbs.sort(key=lambda x: x[0])
        return [i[1] for i in crumbs]

    def breadcrumb_override_active_route(self, **kw):
        """
            Override the class defined breadcrumbs from a view callable

            :param title: String to be used as the override string for the
                          breadcrumb.
            :return: None
        """
        title = kw.get('crumb_title')
        if title is None:
            title = self._crumb_title_

        crumbs = copy.deepcopy(self._breadcrumbs_)
        active = crumbs.get(self._active_route_)
        if active is not None:
            active = list(active)
            active[2] = title
            crumbs.update({self._active_route_: tuple(active)})

        # only reset the crumb if there's a title and an active crumb to
        #  override
        if title and active:
            self._breadcrumbs_ = crumbs

    def get_info(self, **kw):
        """Create the default mapping for the view templates.
        """
        # views can override breadcrumbs established for a base route
        #self.breadcrumb_override_active_route(**kw)

        # override breadcrumbs before setting up navigation
        #info = self._content_navigation(**kw)
        info = {}

        page_title = kw.get('page_title', None)
        if page_title is None:
            kw['page_title'] = self.page_title

        if self.header_icon is not None:
            info.update(dict(header_icon=self.header_icon))

        info.update(dict(
            error=self._error,
            layout=self.layout,
            #section=self.section,
            #section_content_header_css=self.section_content_header_css,
            #admin=self._admin(),
            #manage_patients=self._admin() or self._manage_patients(),
            #assign_programs=self._admin() or self._assign_programs(),
            #customersupport=self._admin() or self.request.customersupport,
            #programassignment=self._admin() or self.request.programassignment,
            #production=self._admin() or self.request.production,
            **kw
        ))
        return info

    def get_action(self):
        return self.__action__

    def get_schema(self, **kw):
        return self.__schema__(**kw)

    @reify
    def form(self):
        form = Form(schema=self.get_schema(),
                    action=self.get_action(),
                    buttons=self.buttons)
        return form

    def leftnav(self, obj, active=None, urls=None):
        """ build the left nav structure for the view

            This can likely be moved into BaseView - and then
            overridden via _urls dict on the subclass from BaseView

        """
        if urls is None:
            urls = self._leftnav_urls()

        for k, v in urls.items():
            if k == active:
                aval = 'active'
            else:
                aval = ''

            attrs = v[1].split(',')
            if len(attrs) == 2:
                uid = attrs[0]
                kw = {uid: getattr(obj, attrs[1])}
            else:
                kw = dict(uid=getattr(obj, attrs[0]))
            url = (v[0], v[2] % {'active': aval,
                                 'href': self.request.route_url(k, **kw)})
            urls[k] = url

        leftnav = urls.values()
        leftnav.sort(key=lambda x: x[0])
        return [i[1] for i in leftnav]

    @reify
    def layout(self):
        renderer = get_renderer("templates/main.pt")
        layout = renderer.implementation().macros['layout']
        return layout

    def listing_view(self, filtered=False, **kw):
        """render a listing of objects for some 'standard list view'

        """
        info = self.get_info(**kw)
        # XXX need to plan for batching or show some other page
        if filtered:
            items = self._get_filtered_listing_items()
        else:
            items = self._get_listing_items()

        error = self.request.GET.get('error', None)
        info.update(dict(items=items, error=error))
        return info


class HomeDashboard(BaseView):

    def __init__(self, request):
        super(HomeDashboard, self).__init__(request)
        self.page_title = 'Home'

    @view_config(route_name='home',
                 renderer='templates/main.pt',
                 permission='view',
                 )
    def home(self):
        """render dashboard home"""
        info = self.get_info()
        return info


@forbidden_view_config(renderer='templates/forbidden.pt',)
def forbidden_view(request):
    # do not allow a user to login if they are already logged in
    if authenticated_userid(request):
        renderer = get_renderer("templates/main.pt")
        info = dict(page_title='Forbidden - Not Allowed',
                    error='Your are not allowed to access this page.',
                    layout=renderer.implementation().macros['layout'],
                    content_lead='Access Denied',
                    noleftnav=True,
                    admin=request._admin,
                    manage_patients=request._manage_patients,
                    assign_programs=request._assign_programs,
                    customersupport=request.customersupport,
                    production=request.production,
                    )
        return info

    loc = request.route_url('login', _query=(('next', request.path),))
    return HTTPFound(location=loc)


@view_config(route_name='logout',
             request_method='GET')
def logout_view(request):
    headers = forget(request)
    loc = request.route_url('login')
    return HTTPFound(location=loc, headers=headers)


def site_layout():
    renderer = get_renderer("templates/main.pt")
    layout = renderer.implementation().macros['layout']
    return layout
