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

    def test_register_page_form_elements(self):
        response = self.client.get(reverse('todo:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form', msg_prefix="Form tag is missing on the register page")
        self.assertContains(response, 'input type="text" name="username"', msg_prefix="Username field is missing")
        self.assertContains(response, 'input type="password" name="password1"', msg_prefix="Password field 1 is missing")
        self.assertContains(response, 'input type="password" name="password2"', msg_prefix="Password field 2 is missing")

    def test_index_page_dark_mode_button_text(self):
        response = self.client.get(reverse('todo:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<button id="theme-toggle"', html=False)
        self.assertContains(response, '>🌙 Dark Mode</button>', html=False, msg_prefix="Dark Mode button text is incorrect or missing")
    def test_template_page_navigation_links(self):
        response = self.client.get(reverse('todo:template'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a href="/">To-Done</a>', msg_prefix="Home link is missing")
        self.assertContains(response, '<a class="tabs" href="/todo">Lists</a>', msg_prefix="Lists link is missing")
        self.assertContains(response, '<a class="tabs" href="/templates">Templates</a>', msg_prefix="Templates link is missing")
    def test_template_page_navigation_links(self):
        response = self.client.get(reverse('todo:template'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a href="/">To-Done</a>', msg_prefix="Home link is missing")
        self.assertContains(response, '<a class="tabs" href="/todo">Lists</a>', msg_prefix="Lists link is missing")
        self.assertContains(response, '<a class="tabs" href="/templates">Templates</a>', msg_prefix="Templates link is missing")
    def test_header_text_on_pages(self):
        pages = ['todo:index', 'todo:template', 'todo:register']
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(reverse(page))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'To-Done', msg_prefix=f"Header text is missing on {page}")
