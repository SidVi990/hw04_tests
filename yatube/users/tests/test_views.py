from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms
from http import HTTPStatus


User = get_user_model()


class UsersPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.templates_pages_names = {
            reverse('users:password_change'):
            'users/password_change_form.html',
            reverse('users:password_change_done'):
            'users/password_change_done.html',
            reverse('users:logout'):
            'users/logged_out.html',
            reverse('users:signup'):
            'users/signup.html',
            reverse('users:login'):
            'users/login.html',
            reverse('users:password_reset_form'):
            'users/password_reset_form.html',
            reverse('users:password_reset_done'):
            'users/password_reset_done.html',
            reverse(
                'users:password_reset_confirm',
                kwargs={'uidb64': '<uidb64>', 'token': '<token>'}):
            'users/password_reset_confirm.html',
            reverse('users:password_reset_complete'):
            'users/password_reset_complete.html',
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_about_page_accessible_by_name(self):
        """URL, генерируемыt при помощи имён namespace:name, доступены"""
        for reverse_name in self.templates_pages_names.keys():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_show_correct_context(self):
        """Шаблон signup сформирован с правильным контекстом."""
        response = self.client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(
                    'form').fields.get(value)
                self.assertIsInstance(form_field, expected)
