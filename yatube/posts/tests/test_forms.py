from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
        )
        cls.user = User.objects.create_user(username='Nemo')
        cls.post = Post.objects.create(
            text='Тестовый пост для проверки работы сервиса.',
            author=User.objects.create_user(username='auth'),
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)

    def test_create_post(self):
        # Валидная форма создает запись в Post.
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Создаем тестовый пост',
            'group': self.group.pk,
            'user': self.user.pk,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        test_post = Post.objects.first()  # Новый пост в базе данных
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # В базе добавляется один новый пост
        self.assertEqual(test_post.text, form_data['text'])
        # Текст созданного поста совпадает со введенными данными
        self.assertEqual(test_post.group.pk, form_data['group'])
        # Группа созданного поста совпадает с выбранной при создании
        self.assertEqual(test_post.author.pk, form_data['user'])
        # Автор поста - пользователь, который его создал
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username}),
        )  # После создания поста срабатывает редирект на профиль автора

    def test_guest_create_post(self):
        # Незарегистрированный пользователь не может создавать записи через форму.
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Гость пришел и написал этот пост',
            'group': self.group.pk,
            'user': self.user.pk,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        # В базе не появилось новых постов
        self.assertFalse(Post.objects.filter(text=form_data['text']).exists())
        # В базе нет поста с текстом от гостя
        self.assertRedirects(response, '/auth/login/?next=/create/')
        # Редирект на страницу входа в аккаунт с переходом к созданию поста

    def test_author_edits_post(self):
        # Валидная форма изменяет запись в Post.
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста отредактирован',
            'group': self.group.pk,
        }
        response = self.authorized_author.post(
            reverse('posts:post_edit', args=({self.post.pk})),
            data=form_data,
            follow=True,
        )
        edited_post = Post.objects.first()
        self.assertEqual(Post.objects.count(), posts_count)
        # Количество постов в базе данных не меняется
        self.assertEqual(edited_post.text, form_data['text'])
        # Текст поста изменился после редактирования
        self.assertEqual(edited_post.group.pk, form_data['group'])
        # Пост после редактирования относится к выбранной группе
        self.assertEqual(edited_post.author.pk, self.post.author.pk)
        # Автор поста - пользователь, который его создал
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}),
        )
        # Редирект на страницу поста

    def test_reader_edits_post(self):
        # Редактирование записи в Post недоступно для не-автора
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Теперь этот пост принадлежит мне!',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=({self.post.pk})),
            data=form_data,
            follow=True,
        )
        attempted_edit = Post.objects.first()
        self.assertEqual(Post.objects.count(), posts_count)
        # Количество постов в базе данных не меняется
        self.assertNotEqual(attempted_edit.text, form_data['text'])
        # Текст поста не изменился после попытки редактирования
        self.assertIsNone(attempted_edit.group)
        # Пост не принадлежит к группе после попытки редактирования
        self.assertNotEqual(attempted_edit.author.pk, self.user.pk)
        # Автор поста - пользователь, который его создал
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}),
        )
        # Редирект на страницу поста
