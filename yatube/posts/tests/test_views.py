from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group
from posts.forms import PostForm

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        groups = []
        for i in range(2):
            groups.append(
                Group.objects.create(
                    title=f'Тестовая группа {i + 1}',
                    slug=f'test_group_{i + 1}',
                    description=f'Тестовое описание {i + 1}',
                )
            )
        cls.post = Post.objects.create(
            text='Тестовый пост для проверки работы сервиса.',
            author=User.objects.create_user(username='auth'),
            group=groups[0],
        )
        cls.group = cls.post.group
        cls.group_2 = groups[1]

    def setUp(self):
        self.user = PostPagesTests.post.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(
        self,
    ):  # URL-адрес использует соответствующий шаблон
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',  # Главная страница
            reverse(
                'posts:group_list',
                kwargs={'slug': self.post.group.slug},  # Страница группы
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'auth'},  # Страница профиля
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk},  # Страница поста
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk},  # Страница изменения поста
            ): 'posts/create_post.html',
            reverse(
                'posts:post_create'  # Страница создания поста
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_uses_correct_context(self):
        # Шаблон главной страницы использует правильный контекст
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title

        self.assertEqual(post_author_0, 'auth')
        self.assertEqual(post_text_0, PostPagesTests.post.text)
        self.assertEqual(post_group_0, PostPagesTests.group.title)
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_group_page_uses_correct_context(self):
        # Шаблон группы использует правильный контекст
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test_group_1'},
            )
        )
        first_object = response.context['group']
        group_title_0 = first_object.title
        group_slug_0 = first_object.slug
        group_description_0 = first_object.description
        self.assertEqual(group_title_0, PostPagesTests.group.title)
        self.assertEqual(group_slug_0, PostPagesTests.group.slug)
        self.assertEqual(group_description_0, PostPagesTests.group.description)
        self.assertEqual(len(response.context["page_obj"]), 1)

    def test_profile_page_uses_correct_context(self):
        # Шаблон профиля использует правильный контекст
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            )
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(
            response.context['profile'].username, self.user.username
        )
        self.assertEqual(post_text_0, PostPagesTests.post.text)
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_post_page_uses_correct_context(self):
        # Шаблон поста использует правильный контекст
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk},
            )
        )
        first_object = response.context['post']
        self.assertEqual(first_object.pk, 1)

    def test_post_create_page_uses_correct_context(self):
        # Шаблон создания поста использует правильный контекст
        response = self.authorized_client.get(reverse('posts:post_create'))
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm)
        self.assertNotIn('is_edit', response.context)
        # Словарь ожидаемых типов полей формы
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_uses_correct_context(self):
        # Шаблон редактирования поста использует правильный контекст
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm)
        self.assertIn('is_edit', response.context)
        # Словарь ожидаемых типов полей формы
        form_fields = {
            'text': [forms.fields.CharField, self.post.text],
            'group': [forms.fields.ChoiceField, self.post.group.pk],
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected[0])
                # Форма отображает данные поста для редактирования
                form_field_includes = response.context['form'][value].value()
                self.assertEqual(form_field_includes, expected[1])

    def test_new_post_gets_to_correct_pages(self):
        # При создании пост отображается только на правильных страницах
        NEW_POST_TEXT = 'Создаем пост в группу'
        form_data = {'text': NEW_POST_TEXT, 'group': self.group.pk}
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        pages = (
            reverse('posts:index'),  # Пост отображается на главной странице...
            reverse(
                'posts:profile',
                kwargs={
                    'username': f'{self.user.username}'
                },  # ...и в профиле автора
            ),
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{self.group.slug}'},  # ...и в группе поста.
            ),
        )
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertContains(response, NEW_POST_TEXT)

        response = self.authorized_client.get(
            reverse(
                'posts:group_list',  # Пост не отображается в чужой группе
                kwargs={'slug': f'{self.group_2.slug}'},
            )
        )
        self.assertNotContains(response, NEW_POST_TEXT)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nemo')
        cls.group = Group.objects.create(
            title='Test group',
            description='Group for paginator tests',
            slug='test_group',
        )
        Post.objects.bulk_create(
            Post(
                text=f'Тест для паджинатора {i}',
                author=cls.user,
                group=cls.group,
            )
            for i in range(13)
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def pages_contain_right_amount_of_records(self):
        # Проверка: количество постов на первой странице равно 10, на второй - 3.
        POST_COUNT = 10
        POST_COUNT_2 = 3
        tests_pages = [(POST_COUNT, 1), (POST_COUNT_2, 2)]
        for posts_on_page, page_number in tests_pages:
            pages = (
                reverse('posts:index'),
                reverse(
                    'posts:profile',
                    kwargs={'username': f'{self.user.username}'},
                ),
                reverse(
                    'posts:group_list', kwargs={'slug': f'{self.group.slug}'}
                ),
            )
            for page in pages:
                with self.subTest(page=page):
                    response = self.authorized_client.get(
                        page + f'?page={page_number}'
                    )
                    count = len(response.context['page_obj'])
                    error_message = (
                        f'Ошибка: на странице {page_number} отображается постов: {count},'
                        f' должно быть: {posts_on_page}'
                    )
                    self.assertEqual(count, posts_on_page, error_message)
