from django.test import override_settings
from rest_framework.test import APITestCase


@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
})
class AuthTests(APITestCase):

    def test_register_and_login(self):
        register_url = '/api/v1/accounts/register/'
        login_url = '/api/v1/accounts/login/'

        payload = {
            'email': 'test@example.com',
            'password': 'strongpass123',
            'name': 'Tester'
        }

        # Register
        resp = self.client.post(register_url, payload, format='json')
        self.assertEqual(resp.status_code, 201, resp.data)
        data = resp.data.get('data', {})
        self.assertEqual(data.get('email'), payload['email'])

        # Login
        resp = self.client.post(login_url, {'email': payload['email'], 'password': payload['password']}, format='json')
        # debug print
        print('\nLOGIN RESPONSE:', resp.status_code, resp.data)
        self.assertEqual(resp.status_code, 200, resp.data)
        # tokens are returned at top-level and refresh is stored in cookie
        self.assertIn('access', resp.data)
        # check refresh cookie exists in client cookie jar
        self.assertTrue(any('refresh_token' in c.key for c in self.client.cookies.values()) or 'refresh_token' in resp.cookies)
