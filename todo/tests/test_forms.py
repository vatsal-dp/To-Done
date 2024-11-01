from django.test import TestCase
from todo.forms import NewUserForm

class NewUserFormTests(TestCase):


    def test_invalid_form(self):
        form = NewUserForm(data={'username': 'testuser', 'email': 'test@example.com', 'password1': 'password123', 'password2': 'differentpassword'})
        self.assertFalse(form.is_valid())

    def test_form_validation_error_message(self):
        form_data = {'username': '', 'email': 'invalid-email'}
        form = NewUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('This field is required.', form.errors['username'])
        self.assertIn('Enter a valid email address.', form.errors['email'])

    def test_email_field_required(self):
        form = NewUserForm(data={
            'username': 'testuser',
            'email': '',  # Leave email empty
            'password1': 'Password@123',
            'password2': 'Password@123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors, "Email field should not be empty")

    # Case to verify password complexity (e.g., password too simple)
    def test_password_complexity(self):
        form = NewUserForm(data={
            'username': 'simpleuser',
            'email': 'simple@example.com',
            'password1': 'password',
            'password2': 'password'
        })
        self.assertFalse(form.is_valid(), "Password complexity check failed")

    # Case to confirm that the form handles a username that already exists
    def test_username_already_exists(self):
        # Create a user with the same username to cause a conflict
        NewUserForm(data={'username': 'duplicateuser', 'email': 'existing@example.com', 'password1': 'Password@123', 'password2': 'Password@123'}).save()
        form = NewUserForm(data={
            'username': 'duplicateuser',  # Duplicate username
            'email': 'new@example.com',
            'password1': 'Password@123',
            'password2': 'Password@123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors, "Username should not allow duplicates")

    # Case for a valid form submission to confirm form saves correctly
    def test_valid_form_submission(self):
        form = NewUserForm(data={
            'username': 'validuser',
            'email': 'valid@example.com',
            'password1': 'Password@123',
            'password2': 'Password@123'
        })
        self.assertTrue(form.is_valid(), "Form should be valid with correct data")

    # Case to check that password confirmation fails when passwords don't match
    def test_password_mismatch(self):
        form = NewUserForm(data={
            'username': 'usermismatch',
            'email': 'mismatch@example.com',
            'password1': 'Password@123',
            'password2': 'DifferentPassword@123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors, "Password mismatch should result in an error")