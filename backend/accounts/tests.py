from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from .models import (
    CustomUser,
    Course,
    Enrollment,
    Question,
    Option,
    QuizResult,
    Achievement,
    UserAchievement,
    Notification,
    Form
)


class CustomUserTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertTrue(self.user.check_password("password123"))

    def test_superuser_creation(self):
        admin = CustomUser.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class CourseTestCase(TestCase):
    def setUp(self):
        self.author = CustomUser.objects.create_user(
            username="author",
            email="author@example.com",
            password="password123"
        )
        self.course = Course.objects.create(
            title="Test Course",
            author=self.author,
            description="A test course description",
            tags="test,course"
        )

    def test_course_creation(self):
        self.assertEqual(self.course.title, "Test Course")
        self.assertEqual(self.course.author, self.author)
        self.assertEqual(self.course.description, "A test course description")
        self.assertEqual(self.course.tags, "test,course")


class EnrollmentTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="student",
            email="student@example.com",
            password="password123"
        )
        self.course = Course.objects.create(
            title="Test Course",
            author=None,
            description="A test course description",
            tags="test,course"
        )
        self.enrollment = Enrollment.objects.create(user=self.user, course=self.course)

    def test_enrollment_creation(self):
        self.assertEqual(self.enrollment.user, self.user)
        self.assertEqual(self.enrollment.course, self.course)


class QuestionAndOptionTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", email="test@example.com", password="password")
        self.course = Course.objects.create(title="Test Course", description="Test Description", author=self.user)
        self.form = Form.objects.create(course=self.course, title="Test Form", description="Test Form Description")
        self.question = Question.objects.create(form=self.form, text="What is Django?")
        self.option = Option.objects.create(question=self.question, text="A web framework", is_correct=True)

    def test_question_and_option_creation(self):
        self.assertEqual(self.question.text, "What is Django?")
        self.assertEqual(self.option.text, "A web framework")
        self.assertTrue(self.option.is_correct)


class QuizResultTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="quiz_taker",
            email="quiz@example.com",
            password="password123"
        )
        self.course = Course.objects.create(
            title="Test Course",
            author=None,
            description="A test course description",
            tags="test,course"
        )
        self.quiz_result = QuizResult.objects.create(
            user=self.user, course=self.course, correct_answers=8
        )

    def test_quiz_result_creation(self):
        self.assertEqual(self.quiz_result.user, self.user)
        self.assertEqual(self.quiz_result.course, self.course)
        self.assertEqual(self.quiz_result.correct_answers, 8)


class AchievementTestCase(TestCase):
    def setUp(self):
        self.achievement = Achievement.objects.create(
            title="First Course Completion",
            description="Complete your first course",
            condition="complete_course_1"
        )

    def test_achievement_creation(self):
        self.assertEqual(self.achievement.title, "First Course Completion")
        self.assertEqual(self.achievement.description, "Complete your first course")
        self.assertEqual(self.achievement.condition, "complete_course_1")


class UserAchievementTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="achiever",
            email="achiever@example.com",
            password="password123"
        )
        self.achievement = Achievement.objects.create(
            title="First Course Completion",
            description="Complete your first course",
            condition="complete_course_1"
        )
        self.user_achievement = UserAchievement.objects.create(
            user=self.user, achievement=self.achievement
        )

    def test_user_achievement_creation(self):
        self.assertEqual(self.user_achievement.user, self.user)
        self.assertEqual(self.user_achievement.achievement, self.achievement)


class CourseEditTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="author",
            email="author@example.com",
            password="password123"
        )
        self.course = Course.objects.create(
            title="Основы Python",
            description="Курс для начинающих",
            tags="программирование, Python",
            content="Введение в Python",
            author=self.user
        )
        self.client.force_login(self.user)
        self.client.force_authenticate(user=self.user)

    def test_edit_course(self):
        url = reverse("edit_course", args=[self.course.id])
        data = {
            "title": "Продвинутый Python",
            "description": "Курс для продвинутых разработчиков",
            "tags": "Python, ООП, асинхронность",
            "content": "ООП в Python, асинхронное программирование, декораторы"
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Продвинутый Python")


class NotificationTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", email="test@example.com", password="password")
        self.client.force_authenticate(user=self.user)

    def test_notification_created_on_level_up(self):
        # Добавляем опыт, чтобы повысить уровень
        self.user.add_experience(5)  # Уровень повысится с 1 до 2

        # Проверяем, что уведомление создано
        notification = Notification.objects.filter(user=self.user).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.message, "Поздравляем! Вы достигли уровня 2.")


class LevelSystemTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", email="test@example.com", password="password")
        self.client.force_authenticate(user=self.user)

    def test_level_up_with_increasing_experience(self):
        # Добавляем опыт для повышения уровня
        self.user.add_experience(5)  # Уровень 1 -> 2
        self.assertEqual(self.user.level, 2)
        self.assertEqual(self.user.experience, 0)

        # Добавляем ещё опыт для следующего уровня
        self.user.add_experience(10)  # Уровень 2 -> 3
        self.assertEqual(self.user.level, 3)
        self.assertEqual(self.user.experience, 0)

        # Добавляем недостаточно опыта для следующего уровня
        self.user.add_experience(7)  # Нужно 15 для уровня 4
        self.assertEqual(self.user.level, 3)
        self.assertEqual(self.user.experience, 7)


class NotificationAPITestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", email="test@example.com", password="password")
        self.client.force_authenticate(user=self.user)

    def test_get_notifications(self):
        # Создаем уведомление
        Notification.objects.create(user=self.user, message="Тестовое уведомление")

        # Отправляем запрос на получение уведомлений
        url = reverse("get_notifications", args=[self.user.id])
        response = self.client.get(url)

        # Проверяем ответ
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["notifications"]), 1)
        self.assertEqual(response.json()["notifications"][0]["message"], "Тестовое уведомление")


class GetCourseQuestionsTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", email="test@example.com", password="password")
        self.course = Course.objects.create(title="Test Course", description="Test Description", author=self.user)
        self.form = Form.objects.create(course=self.course, title="Test Form", description="Test Form Description")
        self.question = Question.objects.create(form=self.form, text="Test Question")
        self.option = Option.objects.create(question=self.question, text="Test Option", is_correct=True)

    def test_get_course_questions(self):
        url = reverse("get_course_questions", args=[self.course.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["forms"]), 1)
        self.assertEqual(response.json()["forms"][0]["questions"][0]["text"], "Test Question")
        self.assertEqual(response.json()["forms"][0]["questions"][0]["options"][0]["text"], "Test Option")


class CheckAnswersTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", email="test@example.com", password="password")
        self.course = Course.objects.create(title="Test Course", description="Test Description", author=self.user)
        self.form = Form.objects.create(course=self.course, title="Test Form", description="Test Form Description")
        self.question = Question.objects.create(form=self.form, text="Test Question")
        self.option = Option.objects.create(question=self.question, text="Test Option", is_correct=True)
        self.client.force_authenticate(user=self.user)

    def test_check_answers(self):
        data = {
            "user_id": self.user.id,
            "answers": {
                str(self.question.id): self.option.id,
            }
        }

        url = reverse("check_answers", args=[self.course.id])
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["correct"], 1)
        self.assertEqual(response.json()["total"], 1)


class FormTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", email="test@example.com", password="password")
        self.course = Course.objects.create(title="Test Course", description="Test Description", author=self.user)
        self.client.force_authenticate(user=self.user)

    def test_create_form(self):
        # Данные для создания формы
        data = {
            "title": "Test Form",
            "description": "Test Form Description",
        }

        # Отправляем запрос на создание формы
        url = reverse("create_form", args=[self.course.id])
        response = self.client.post(url, data, format="multipart")

        # Проверяем ответ
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["message"], "Form created successfully")

        # Проверяем, что форма создана в базе данных
        form = Form.objects.filter(course=self.course).first()
        self.assertIsNotNone(form)
        self.assertEqual(form.title, "Test Form")
        self.assertEqual(form.description, "Test Form Description")


class QuestionTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", email="test@example.com", password="password")
        self.course = Course.objects.create(title="Test Course", description="Test Description", author=self.user)
        self.form = Form.objects.create(course=self.course, title="Test Form", description="Test Form Description")
        self.client.force_authenticate(user=self.user)

    def test_add_question_with_image(self):
        # Создаем тестовое изображение
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")

        # Данные для добавления вопроса
        data = {
            "text": "Test Question",
            "image": image,
        }

        # Отправляем запрос на добавление вопроса
        url = reverse("add_question_to_form", args=[self.form.id])
        response = self.client.post(url, data, format="multipart")

        # Проверяем ответ
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["message"], "Question added successfully")

        # Проверяем, что вопрос создан в базе данных
        question = Question.objects.filter(form=self.form).first()
        self.assertIsNotNone(question)
        self.assertEqual(question.text, "Test Question")
        self.assertIsNotNone(question.image)


class OptionTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", email="test@example.com", password="password")
        self.course = Course.objects.create(title="Test Course", description="Test Description", author=self.user)
        self.form = Form.objects.create(course=self.course, title="Test Form", description="Test Form Description")
        self.question = Question.objects.create(form=self.form, text="Test Question")
        self.client.force_authenticate(user=self.user)

    def test_add_option_with_image(self):
        # Создаем тестовое изображение
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")

        # Данные для добавления варианта ответа
        data = {
            "text": "Test Option",
            "is_correct": True,
            "image": image,
        }

        # Отправляем запрос на добавление варианта ответа
        url = reverse("add_option_to_question", args=[self.question.id])
        response = self.client.post(url, data, format="multipart")

        # Проверяем ответ
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["message"], "Option added successfully")

        # Проверяем, что вариант ответа создан в базе данных
        option = Option.objects.filter(question=self.question).first()
        self.assertIsNotNone(option)
        self.assertEqual(option.text, "Test Option")
        self.assertTrue(option.is_correct)
        self.assertIsNotNone(option.image)


class FormAPITestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", email="test@example.com", password="password")
        self.course = Course.objects.create(title="Test Course", description="Test Description", author=self.user)
        self.form1 = Form.objects.create(course=self.course, title="Form 1", description="Description 1")
        self.form2 = Form.objects.create(course=self.course, title="Form 2", description="Description 2")
        self.client.force_authenticate(user=self.user)

    def test_get_course_forms(self):
        # Отправляем запрос на получение форм для курса
        url = reverse("get_course_forms", args=[self.course.id])
        response = self.client.get(url)

        # Проверяем ответ
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["forms"]), 2)
        self.assertEqual(response.json()["forms"][0]["title"], "Form 2")  # Последняя форма
        self.assertEqual(response.json()["forms"][1]["title"], "Form 1")  # Первая форма

