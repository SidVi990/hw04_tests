from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms
from http import HTTPStatus

from ..models import Post, Group

User = get_user_model()


class PostsPagesTests(TestCase):
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
            group=cls.group
        )
        cls.templates_pages_names = {
            reverse('posts:index'):
            'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': cls.user.username}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': cls.post.id}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': cls.post.id}):
            'posts/create_post.html',
            reverse('posts:post_create'):
            'posts/create_post.html',
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

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.group, self.post.group)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.id, self.post.id)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.group, self.post.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.post.author)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        first_object = response.context.get('post')
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.post.author)

    def test_create_edit_post_show_correct_context(self):
        """Шаблоны post_create и post_edit
            сформированы с правильным контекстом."""
        post_create_edit_templates = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        for templates in post_create_edit_templates:
            with self.subTest(templates=templates):
                response = self.authorized_client.get(templates)
                form_fields = {
                    'text': forms.fields.CharField,
                    'group': forms.fields.ChoiceField,
                }
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get(
                            'form').fields.get(value)
                        self.assertIsInstance(form_field, expected)

    def test_pages_contain_post(self):
        """Проверяем появляется ли пост с
            определенной группой на нужных страницах"""
        pages_names = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        )
        for name in pages_names:
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.text, self.post.text)
                self.assertEqual(first_object.group, self.post.group)


class PostPaginatorsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.bulk_create(
            [
                Post(
                    text=f'Тестовый пост #{n}',
                    author=cls.user,
                    group=cls.group,
                )
                for n in range(13)
            ]
        )
        cls.pages_names = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={'username': cls.user.username}),
        )

    def test_first_pages_contains_ten_records(self):
        """Тестируем paginator на первых страницах"""
        for name in self.pages_names:
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_pages_contains_three_records(self):
        """Тестируем paginator на вторых страницах"""
        for name in self.pages_names:
            with self.subTest(name=name):
                response = self.client.get(name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
