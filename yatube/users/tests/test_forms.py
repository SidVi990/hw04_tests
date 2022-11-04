from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class UsersCreationFormTests(TestCase):
    def test_create_user(self):
        """Валидная форма создаёт нового пользователя"""
        posts_count = User.objects.count()

        form_data = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'auth',
            'email': 'testemail@yatube.ru',
            'password1': 'SuperDifficultPassword1',
            'password2': 'SuperDifficultPassword1',
        }
        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), posts_count + 1)
