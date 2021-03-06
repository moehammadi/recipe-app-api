from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@admin.com',
            password='admin@123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            password='test@123',
            name='Test User'
        )

    def test_users_listed(self):
        """
        Test that users are listed in the user page
        """
        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)
        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    # def test_user_change_page(self):
    #     """
    #     Test that the user edit page works
    #     """
    #     url = reverse('admin:core_user_changelist', args=[self.user.id])
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
