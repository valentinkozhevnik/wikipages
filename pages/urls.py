from django.conf.urls import patterns, url, include
from .utils import CoreRoute
from .views import PagesViewSet

router = CoreRoute()
router.register(r'pages', PagesViewSet, base_name='pages')


urlpatterns = patterns(
    '',
    url(r'', include(router.get_urls()))
)