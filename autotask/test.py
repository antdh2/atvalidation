from django.test import Client, TestCase

class TestLoggedUser(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user('test_user', 'user@test.net', 'secret')
        self.user.save()
        self.client.login(username='test_user', password='secret')

    def tearDown(self):
        self.user.delete()

    def test_logged_user_get_homepage(self):
        response = self.client.get(reverse('/'), follow=True)
        self.assertEqual(response.status_code, 200)
