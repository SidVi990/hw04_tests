from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создаёт новый пост"""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
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
        new_post = Post.objects.last()
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.group, self.group)

    def test_edit_post(self):
        """Валидная форма редактирует существующий пост"""
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group
        )
        group = Group.objects.create(
            title='Ещё одна тестовая группа',
            slug='another-test-slug',
            description='Тестовое описание',
        )
        form_data = {
            'text': 'Измененный тестовый текст',
            'group': group.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(str(post.id))),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(str(post.id)))
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text']
            ).exists()
        )

        old_group_response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.group.slug,))
        )
        self.assertEqual(
            old_group_response.context['page_obj'].paginator.count, 0
        )
        new_group_response = self.authorized_client.get(
            reverse('posts:group_list', args=(group.slug,))
        )
        self.assertEqual(
            new_group_response.context['page_obj'].paginator.count, 1
        )
