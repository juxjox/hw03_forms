from django.urls import path
from . import views

app_name = "posts"


urlpatterns = [
    # Главная страница
    path("", views.index, name="index"),
    # Все посты сообщества
    path("group/<slug:slug>/", views.posts, name="group_list"),
    # Все посты пользователя
    path("profile/<str:username>/", views.profile, name="profile"),
    # Страница отдельного поста
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    # Страница создания поста
    path("create/", views.post_create, name="post_create"),
    # Страница редактирования поста
    path("posts/<int:post_id>/edit/", views.post_edit, name="post_edit"),
]
