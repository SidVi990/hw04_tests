from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.templates_url_names = {
            '/auth/password_change/':
            'users/password_change_form.html',
            '/auth/password_change/done/':
            'users/password_change_done.html',
            '/auth/logout/':
            'users/logged_out.html',
            '/auth/signup/':
            'users/signup.html',
            '/auth/login/':
            'users/login.html',
            '/auth/password_reset/':
            'users/password_reset_form.html',
            '/auth/password_reset/done/':
            'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/':
            'users/password_reset_confirm.html',
            '/auth/reset/done/':
            'users/password_reset_complete.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exists_at_desired_location(self):
        """Проверка доступности адресов."""
        for address in self.templates_url_names.keys():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_anonymous_on_admin_login(self):
        """Страницы перенаправитят анонимного
        пользователя на страницу логина.
        """
        urls_redirect = {
            '/auth/password_change/':
            '/auth/login/?next=/auth/password_change/',
            '/auth/password_change/done/':
            '/auth/login/?next=/auth/password_change/done/',
        }
        for address, redirect in urls_redirect.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, (redirect))

    def test_urls_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        for address, template in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
