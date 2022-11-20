from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Post, Group

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(
                username='Nemo',
            ),
            text='Тестовый текст для проверки адресов и шаблонов проекта',
            id='1',
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
        )

        cls.check_urls_templates_and_status = {
            (
                '/',
                'posts/index.html',
                HTTPStatus.OK,
            ),  # Главная страница доступна всем
            (
                '/group/test_group/',
                'posts/group_list.html',
                HTTPStatus.OK,
            ),  # Страница группы доступна всем
            (
                '/profile/Nemo/',
                'posts/profile.html',
                HTTPStatus.OK,
            ),  # Страница профиля доступна всем
            (
                '/create/',
                'posts/create_post.html',
                HTTPStatus.OK,
                'author',
            ),  # Страница создания поста для авторизованного пользователя
            (
                '/create/',
                'users/login.html',
                HTTPStatus.FOUND,
                'redirect',
            ),  # Страница создания поста для неавторизованного пользователя
            (
                '/posts/1/',
                'posts/post_detail.html',
                HTTPStatus.OK,
            ),  # Страница деталей поста доступна всем
            (
                '/posts/1/edit/',
                'posts/create_post.html',
                HTTPStatus.OK,
                'author',
            ),  # Страница редактирования поста для автора
            (
                '/posts/1/edit/',
                'posts/post_detail.html',
                HTTPStatus.FOUND,
                'redirect',
            ),  # Страница редактирования поста для читателя(не автор)
            (
                '/unexisting_page/',
                'template_check_skip',
                HTTPStatus.NOT_FOUND,
                'redirect',
            ),  #  Несуществующая страница - ошибка 404
        }

    def setUp(self):
        self.guest_client = Client()
        self.user = self.post.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_new_http_response(self):  # Проверяем HTTPResponse
        for (
            address,
            _,
            status_code,
            *z,
        ) in URLTests.check_urls_templates_and_status:
            if 'author' in z:
                with self.subTest(address=address):
                    response = self.authorized_client.get(address)
                    self.assertEqual(response.status_code, status_code)
            else:
                with self.subTest(address=address):
                    response = self.guest_client.get(address)
                    self.assertEqual(response.status_code, status_code)

    def test_url_uses_correct_template(self):  # Проверяем шаблоны
        for address, template, *z in URLTests.check_urls_templates_and_status:
            if 'author' in z:
                with self.subTest(address=address):
                    response = self.authorized_client.get(address)
                    self.assertTemplateUsed(response, template)
            elif 'redirect' not in z:
                with self.subTest(address=address):
                    response = self.guest_client.get(address)
                    self.assertTemplateUsed(response, template)
