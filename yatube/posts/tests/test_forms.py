from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создаёт новый пост"""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Валидная форма редактирует существующий пост"""
        form_data = {
            'text': 'Измененный тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(str(self.post.id))),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(str(self.post.id)))
        )
        self.assertTrue(
            Post.objects.filter(
                text='Измененный тестовый текст'
            ).exists()
        )
