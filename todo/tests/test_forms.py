from django.test import TestCase
from todo.forms import NewUserForm

class NewUserFormTests(TestCase):

    def test_invalid_form(self):
        form = NewUserForm(data={'username': 'testuser', 'email': 'test@example.com', 'password1': 'password123', 'password2': 'differentpassword'})
        self.assertFalse(form.is_valid())
