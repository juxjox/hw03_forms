from django.db import models
from django.forms import ModelForm, Textarea
from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["text", "group"]
        labels = {
            "group": ("Группа"),
            "text": ("Текст поста"),
        }
        help_texts = {
            "text": "Текст нового поста",
            "group": "Группа, к которой будет относиться пост",
        }
