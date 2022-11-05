from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus

from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
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
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
            '/create/': '/auth/login/?next=/create/',
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

    def test_page_not_found(self):
        """Запрос к несуществующей странице возвращает ошибку 404"""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_edit_page_is_redirect_guest_user(self):
        """Страница редактирования поста перенаправит
            анонимного пользователя на страницу авторизации"""
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, ('/auth/login/?next=/posts/1/edit/'))

    def test_edit_page_is_available_only_to_the_author(self):
        """Страница редактирования поста доступна только автору"""
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, ('/posts/1/'))

    def test_edit_page_template_for_authorized_user(self):
        """Страница редактирования поста
            для автора использует правильный щаблон"""
        response = self.authorized_client.get('/posts/1/edit/', follow=True)
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_create_page_is_available_only_to_authorized_user(self):
        """Страница создания поста доступна только
            зарегистрированному пользователю"""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, ('/auth/login/?next=/create/'))
