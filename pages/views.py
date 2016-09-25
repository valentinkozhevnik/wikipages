from django.http import Http404
from pages.serializers import EditPagesSerializer, PagesListSerializer, PagesVersionListSerializer
from pages.utils import many_lockup_route
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import PagesStorage, PagesVersionStorage



class PagesViewSet(ModelViewSet):
    model = PagesStorage
    queryset = PagesStorage.objects.filter(version__isnull=False)
    serializer_class = PagesListSerializer
    paginate_by = 10

    @list_route(methods=['post'])
    def create(self, request, *args, **kwargs):
        serializer = EditPagesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'result': {
            'id': serializer.instance.id
        }})

    @detail_route(methods=['post'])
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = EditPagesSerializer(
            instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'result': 'OK'})

    @detail_route(methods=['get'], url_path=r'version/list')
    def version_list(self, request, pk, *args, **kwargs):
        instance = self.get_object()
        self.serializer_class = PagesVersionListSerializer
        self.queryset = instance.versions.all()
        return super(PagesViewSet, self).list(request, *args, **kwargs)

    @many_lockup_route(methods=['get'],
                       url_path='version-retrieve',
                       extra_url=r'version/(?P<version_id>\d+)')
    def version_item(self, request, pk, version_id, *args, **kwargs):
        instance = self.get_object()
        try:
            version = instance.versions.get(id=version_id)
        except PagesVersionStorage.DoesNotExist:
            raise Http404()
        serializer = PagesVersionListSerializer(instance=version, many=False)
        return Response({'result': serializer.data})

    @detail_route(methods=['get'], url_path=r'version/current')
    def version_current(self, request, pk, *args, **kwargs):
        instance = self.get_object()
        version = instance.version
        serializer = PagesVersionListSerializer(instance=version, many=False)
        return Response({'result': serializer.data})

    @many_lockup_route(methods=['post'],
                       url_path='version-set-current',
                       extra_url=r'version/(?P<version_id>\d+)/set_current')
    def version_set_current(self, request, pk, version_id, *args, **kwargs):
        instance = self.get_object()
        try:
            version = instance.versions.get(id=version_id)
        except PagesVersionStorage.DoesNotExist:
            raise Http404()
        page = version.page
        page.version = version
        page.save()
        return Response({'result': 'OK'})