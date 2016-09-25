from django.core.urlresolvers import reverse
from django.test import TestCase


class CRUDTest(TestCase):
    def test_list(self):
        url = reverse('pages-list')
        self.assertEqual('/api/pages/list', url)
        response = self.client.get(url)
        _ = response.data
        assert response

    def test_create(self):
        url = reverse('pages-create')
        self.assertEqual('/api/pages/create', url)
        response = self.client.post(url, data={'title': 'ok', 'body': 'ok'})
        data = dict(response.data)
        self.assertTrue('result' in data)
        self.assertTrue('id' in data['result'])
        pk = data['result']['id']
        url_get = reverse('pages-detail', kwargs={'pk': pk})
        self.assertEqual('/api/pages/%s' % pk, url_get)
        response = self.client.get(url_get)
        data = dict(response.data)
        self.assertEqual(data['title'], 'ok')
        self.assertEqual(data['body'], 'ok')

    def test_update(self):
        url = reverse('pages-create')
        self.assertEqual('/api/pages/create', url)
        response = self.client.post(url, data={'title': 'ok', 'body': 'ok'})
        data = dict(response.data)
        self.assertTrue('result' in data)
        self.assertTrue('id' in data['result'])
        pk = data['result']['id']
        url_get = reverse('pages-detail', kwargs={'pk': pk})
        self.assertEqual('/api/pages/%s' % pk, url_get)
        response = self.client.get(url_get)
        data = dict(response.data)
        self.assertEqual(data['title'], 'ok')
        self.assertEqual(data['body'], 'ok')
        url_update = reverse('pages-update', kwargs={'pk': pk})
        self.assertEqual('/api/pages/%s/update' % pk, url_update)
        response = self.client.post(url_update,
                                    data={'title': 'ok2', 'body': 'ok2'})
        assert response
        url_get = reverse('pages-detail', kwargs={'pk': pk})
        self.assertEqual('/api/pages/%s' % pk, url_get)
        response = self.client.get(url_get)
        data = dict(response.data)
        self.assertEqual(data['title'], 'ok2')
        self.assertEqual(data['body'], 'ok2')

    def test_version_list(self):
        pk = 1
        url = reverse('pages-create')
        self.assertEqual('/api/pages/create', url)
        _ = self.client.post(url, data={'title': 'ok', 'body': 'ok'})
        url_update = reverse('pages-update', kwargs={'pk': pk})
        self.assertEqual('/api/pages/%s/update' % pk, url_update)
        _ = self.client.post(
            url_update, data={'title': 'ok2', 'body': 'ok2'})
        _ = self.client.post(
            url_update, data={'title': 'ok3', 'body': 'ok3'})
        _ = self.client.post(
            url_update, data={'title': 'ok4', 'body': 'ok4'})

        url = reverse('pages-version-list', kwargs={'pk': pk})
        self.assertEqual('/api/pages/1/version/list', url)
        response = self.client.get(url)
        data = dict(response.data)
        new_ver = data['results'][1]['id']
        self.assertEqual(len(data['results']), 4)

        url = reverse('pages-version-current', kwargs={'pk': pk})
        self.assertEqual('/api/pages/1/version/current', url)
        response = self.client.get(url)
        data = dict(response.data)
        self.assertEqual(data['result']['title'], 'ok4')

        url = reverse('pages-version-set-current',
                      kwargs={'pk': pk, 'version_id': new_ver})
        self.assertEqual('/api/pages/1/version/%s/set_current' % new_ver, url)
        response = self.client.post(url, data={})
        data = dict(response.data)

        url = reverse('pages-version-current', kwargs={'pk': pk})
        self.assertEqual('/api/pages/1/version/current', url)
        response = self.client.get(url)
        data = dict(response.data)
        self.assertEqual(data['result']['id'], new_ver)
