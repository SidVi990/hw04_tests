from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

    def setUp(self):
        self.guest_client = Client()

    def test_urls_exists_at_desired_location(self):
        """Проверка доступности адресов."""
        for address in self.templates_url_names.keys():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        for address, template in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)


class AboutViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.templates_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
    
    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени static_pages:about, доступен."""
        for reverse_name in self.templates_names.keys():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_page_uses_correct_template(self):
        """При запросе к staticpages:about
        применяется шаблон staticpages/about.html."""
        for reverse_name, template in self.templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
