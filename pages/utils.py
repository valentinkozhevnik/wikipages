from collections import namedtuple
from rest_framework.routers import DynamicDetailRoute, DynamicListRoute, \
    DefaultRouter, flatten, Route


ManyLockupRoute = namedtuple('ManyLockupRoute', 'url name initkwargs')


class CoreRoute(DefaultRouter):
    routes = [
        # List route.
        Route(
            url=r'^{prefix}/list{trailing_slash}$',
            mapping={
                'get': 'list',
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        # Dynamically generated list routes.
        # Generated using @list_route decorator
        # on methods of the viewset.
        DynamicListRoute(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
        # Dynamically generated detail routes.
        # Generated using @detail_route decorator on methods of the viewset.
        DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
        ManyLockupRoute(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]

    include_root_view = False
    include_format_suffixes = False

    def __init__(self):
        super(CoreRoute, self).__init__()
        self.trailing_slash = '/?'

    def get_lookup_regex(self, viewset, lookup_prefix=''):
        base_regex = '(?P<{lookup_prefix}{lookup_field}>{lookup_value})'
        lookup_field = getattr(viewset, 'lookup_field', 'pk')
        lookup_value = getattr(viewset, 'lookup_value_regex', '\d+')
        return base_regex.format(
            lookup_prefix=lookup_prefix,
            lookup_field=lookup_field,
            lookup_value=lookup_value
        )

    def get_routes(self, viewset):
        """
        Augment `self.routes` with any dynamically generated routes.

        Returns a list of the Route namedtuple.
        """

        known_actions = flatten([
            route.mapping.values() for route in self.routes if isinstance(
                route, Route)])

        detail_routes = []
        list_routes = []
        many_lockup_routers = []
        catalog = getattr(viewset, 'catalog', None)
        for methodname in dir(viewset):
            attr = getattr(viewset, methodname)

            httpmethods = getattr(attr, 'bind_to_methods', None)
            if httpmethods and catalog and hasattr(catalog, methodname):
                info = getattr(catalog, methodname)
                router = info.pop('router')
                setattr(viewset, methodname, router(**info)(attr))

            detail = getattr(attr, 'detail', True)
            many_lockup = getattr(attr, 'many_lockup', False)
            if httpmethods:
                httpmethods = [method.lower() for method in httpmethods]
                if methodname in known_actions:
                    raise Exception('Cannot use @detail_route or @list_route '
                                    'decorators on method "%s" '
                                    'as it is an existing route' % methodname)
                if many_lockup:
                    many_lockup_routers.append((httpmethods, methodname))
                elif detail:
                    detail_routes.append((httpmethods, methodname))
                else:
                    list_routes.append((httpmethods, methodname))

        ret = []
        for route in self.routes:
            if isinstance(route, DynamicDetailRoute):
                # Dynamic detail routes (@detail_route decorator)
                for httpmethods, methodname in detail_routes:
                    method_kwargs = getattr(viewset, methodname).kwargs
                    url_path = method_kwargs.pop(
                        "url_path", None) or methodname
                    initkwargs = route.initkwargs.copy()
                    initkwargs.update(method_kwargs)
                    ret.append(Route(
                        url=replace_methodname(route.url, url_path),
                        mapping=dict(
                            (htmeth, methodname) for htmeth in httpmethods),
                        name=replace_methodname(route.name, url_path),
                        initkwargs=initkwargs,
                    ))
            elif isinstance(route, DynamicListRoute):
                # Dynamic list routes (@list_route decorator)
                for httpmethods, methodname in list_routes:
                    method_kwargs = getattr(viewset, methodname).kwargs
                    url_path = method_kwargs.pop(
                        "url_path", None) or methodname
                    initkwargs = route.initkwargs.copy()
                    initkwargs.update(method_kwargs)
                    ret.append(Route(
                        url=replace_methodname(route.url, url_path),
                        mapping=dict(
                            (htmeth, methodname) for htmeth in httpmethods),
                        name=replace_methodname(route.name, url_path),
                        initkwargs=initkwargs,
                    ))
            elif isinstance(route, ManyLockupRoute):
                for httpmethods, methodname in many_lockup_routers:
                    method_kwargs = getattr(viewset, methodname).kwargs
                    url_path = method_kwargs.pop(
                        "url_path", None) or methodname
                    extra_url = method_kwargs.pop(
                        "extra_url", None) or url_path
                    initkwargs = route.initkwargs.copy()
                    initkwargs.update(method_kwargs)
                    ret.append(Route(
                        url=replace_methodname(route.url, extra_url),
                        mapping=dict(
                            (htmeth, methodname) for htmeth in httpmethods),
                        name=replace_methodname(route.name, url_path),
                        initkwargs=initkwargs,
                    ))
            else:
                ret.append(route)

        return ret


def many_lockup_route(methods=None, **kwargs):
    methods = ['get'] if (methods is None) else methods

    def decorator(func):
        func.bind_to_methods = methods
        func.many_lockup = True
        func.extra_url = None
        func.kwargs = kwargs
        return func
    return decorator


def replace_methodname(format_string, methodname):
    """
    Partially format a format_string, swapping out any
    '{methodname}' or '{methodnamehyphen}' components.
    """
    methodnamehyphen = methodname.replace('_', '-').replace('/', '-')
    ret = format_string
    ret = ret.replace('{methodname}', methodname)
    ret = ret.replace('{methodnamehyphen}', methodnamehyphen)
    return ret
