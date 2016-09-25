from django.db import models

_app_label = 'pages'


class PagesStorage(models.Model):
    version = models.OneToOneField('pages.PagesVersionStorage')

    class Meta:
        db_table = 'pages_active_storage'
        app_label = _app_label


class PagesVersionStorage(models.Model):
    page = models.ForeignKey('pages.PagesStorage', related_name='versions')
    title = models.CharField(max_length=256)
    body = models.TextField()

    class Meta:
        db_table = 'pages_version_storage'
        app_label = _app_label

    @property
    def is_current(self):
        return self.page.version_id == self.id