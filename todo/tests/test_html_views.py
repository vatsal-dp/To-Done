from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class HTMLViewsTests(TestCase):
    def setUp(self):
        # Create a test user and log them in
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_template_page_renders_correctly(self):
        response = self.client.get(reverse('todo:template'))
        self.assertEqual(response.status_code, 200)
    
    def test_index_page_renders_correctly(self):
        response = self.client.get(reverse('todo:index'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_renders_correctly(self):
        response = self.client.get(reverse('todo:register'))
        self.assertEqual(response.status_code, 200)

    def test_dark_mode_button_exists(self):
        response = self.client.get(reverse('todo:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="theme-toggle"')
