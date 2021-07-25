from django.test import TestCase

from ..models import User, Group, Post, Comment, Follow

TEXT = "Текст"
TITLE = "Название"
SLUG = "test-slug"


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username="test_user_1")
        cls.user_2 = User.objects.create_user(username="test_user_2")
        cls.post = Post.objects.create(text=TEXT)
        cls.group = Group.objects.create(title=TITLE, slug=SLUG)
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user_1,
            text=TEXT
        )
        cls.follow = Follow.objects.create(user=cls.user_1, author=cls.user_2)

    def test_object_name_is_title_field(self):
        """Поле title совпадает с ожидаемымы."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_post_object_name_title_have_15_symbols(self):
        """Правильно отображается поле __str__ в модели Post."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_comment_object_name_title_have_15_symbols(self):
        """Правильно отображается поле __str__ в модели Comment."""
        comment = PostModelTest.comment
        expected_object_name = comment.text[:15]
        self.assertEqual(expected_object_name, str(comment))
