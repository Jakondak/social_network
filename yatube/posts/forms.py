from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        labels = {"text": "текст", "group": "группа", "image": "картинка"}
        help_texts = {
            "text": ("Напишете любой текст без мата"),
            "group": ("А тут можно и с матом")
        }

    def clean_text(self):
        data = self.cleaned_data["text"]
        if not data:
            raise forms.ValidationError("Введите текст")
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        labels = {"test": "текст"}
        help_texts = {
            "text": ("Напишете любой текст без мата"),
        }
