from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from .models import CustomUser, Course, Enrollment, Option, Question, QuizResult, Achievement, UserAchievement, Form
import json
from django.db.models import Sum, Count, F


@csrf_exempt
def register(request):
    if request.method == "POST":
        try:
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            password2 = request.POST.get("password2")
            profile_photo = request.FILES.get("profile_photo")

            if not all([username, email, password, password2, profile_photo]):
                return JsonResponse({"error": "All fields are required"}, status=400)

            if password != password2:
                return JsonResponse({"error": "Passwords do not match"}, status=400)

            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({"error": "Username already taken"}, status=400)

            profile_photo_path = None
            if profile_photo:
                profile_photo_path = default_storage.save(
                    f"profile_photos/{profile_photo.name}", profile_photo
                )

            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            if profile_photo_path:
                user.profile_photo = profile_photo_path
            user.save()

            return JsonResponse({"message": "User registered successfully"}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)


@csrf_exempt
def login_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return JsonResponse(
                    {"error": "Username and password are required"}, status=400
                )

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                response_data = {
                    "userid": user.id,
                }
                return JsonResponse(response_data, status=200)

            else:
                return JsonResponse({"error": "Invalid credentials"}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)


@csrf_exempt
def profile_view(request):
    userid = request.GET.get("userid")
    if not userid:
        return JsonResponse({"error": "userid is required"}, status=400)

    user = get_object_or_404(CustomUser, id=userid)

    profile_photo_url = (
        request.build_absolute_uri(user.profile_photo.url)
        if user.profile_photo
        else None
    )

    data = {
        "id": user.id,
        "is_superuser": user.is_superuser,
        "username": user.username,
        "email": user.email,
        "profile_photo": profile_photo_url,
        "level": user.level,  # Новое поле
        "experience": user.experience,  # Новое поле
    }
    return JsonResponse(data, status=200)


@csrf_exempt
def create_course(request):
    if request.method == "POST":
        try:
            body = request.body.decode("utf-8")
            data = json.loads(body)
            course = Course.objects.create(
                title=data.get("title"),
                description=data.get("description"),
                tags=data.get("tags"),
                content=data.get("content"),
                author=request.user if request.user.is_authenticated else None,
            )
            course.save()
            return JsonResponse({"message": "Course created successfully"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def enroll_course(request, course_id):
    if request.method == "POST":
        try:
            course = get_object_or_404(Course, id=course_id)

            data = json.loads(request.body)
            user_id = data.get("user_id")

            if not user_id:
                return JsonResponse({"error": "User ID is required"}, status=400)

            user = get_object_or_404(CustomUser, id=user_id)

            if Enrollment.objects.filter(course=course, user=user).exists():
                return JsonResponse(
                    {"error": "You are already enrolled in this course"}, status=400
                )

            Enrollment.objects.create(course=course, user=user)
            return JsonResponse(
                {"message": f"You have successfully enrolled in {course.title}"}, status=200
            )
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)


def user_enrolled_courses(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    user_courses = Course.objects.filter(enrollments__user=user)

    courses_data = []
    for course in user_courses:
        courses_data.append(
            {
                "id": course.id,
                "title": course.title,
            }
        )

    return JsonResponse({"courses": courses_data}, status=200)


def courses_list(request):
    courses = Course.objects.all().values(
        "id", "title", "description", "tags", "content"
    )
    return JsonResponse(list(courses), safe=False, status=200)


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return JsonResponse(
        {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "tags": course.tags,
            "content": course.content,
        },
        status=200,
    )


User = get_user_model()


@csrf_exempt
def edit_user(request, user_id):
    if request.method in ["POST", "PUT"]:
        try:
            user = get_object_or_404(CustomUser, id=user_id)

            if request.content_type == "application/json":
                data = json.loads(request.body.decode("utf-8"))
                user.username = data.get("username", user.username)
                user.email = data.get("email", user.email)

            elif request.content_type.startswith("multipart/form-data"):
                user.username = request.POST.get("username", user.username)
                user.email = request.POST.get("email", user.email)
                if "profile_photos" in request.FILES:
                    user.profile_photo = request.FILES["profile_photos"]

            user.save()

            return JsonResponse(
                {
                    "status": "success",
                    "message": "User updated successfully",
                    "user_id": user.id,
                }
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Invalid JSON payload",
                    "status_code": 400,
                },
                status=400,
            )

        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": str(e), "status_code": 500}, status=500
            )

    return JsonResponse(
        {
            "status": "error",
            "message": f"{request.method} method not allowed",
            "status_code": 405,
        },
        status=405,
    )


@csrf_exempt
def delete_user(request, user_id):
    if request.method == "DELETE":
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return JsonResponse(
                {"message": "Пользователь успешно удалён."},
                status=200,
                json_dumps_params={"ensure_ascii": False},
            )
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "Пользователь не найден."},
                status=404,
                json_dumps_params={"ensure_ascii": False},
            )
    return JsonResponse(
        {"error": "Метод запроса должен быть DELETE."},
        status=400,
        json_dumps_params={"ensure_ascii": False},
    )


def count_user_correct_answers(request):
    users = CustomUser.objects.all()

    user_correct_answers = []

    for user in users:
        correct_answers_sum = QuizResult.objects.filter(user=user).aggregate(total_correct=Sum('correct_answers'))['total_correct'] or 0

        user_correct_answers.append(
            {
                "user_id": user.id,
                "username": user.username,
                "correct_answers": correct_answers_sum,
            }
        )

    return JsonResponse({"user_correct_answers": user_correct_answers}, status=200)


@csrf_exempt
def create_form(request, course_id):
    if request.method == "POST":
        try:
            course = get_object_or_404(Course, id=course_id)
            data = request.POST
            files = request.FILES

            form = Form.objects.create(
                course=course,
                title=data.get("title"),
                description=data.get("description"),
            )

            if "image" in files:
                form.image = files["image"]
                form.save()

            return JsonResponse({"message": "Form created successfully", "form_id": form.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def get_course_forms(request, course_id):
    if request.method == "GET":
        try:
            course = get_object_or_404(Course, id=course_id)
            forms = course.forms.all().order_by("-id")  # Сортировка по id в порядке убывания
            response_data = []

            for form in forms:
                form_data = {
                    "id": form.id,
                    "title": form.title,
                    "description": form.description,
                    "image": request.build_absolute_uri(form.image.url) if form.image else None,
                }
                response_data.append(form_data)

            return JsonResponse({"forms": response_data}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def add_question_to_form(request, form_id):
    if request.method == "POST":
        try:
            form = get_object_or_404(Form, id=form_id)
            data = request.POST
            files = request.FILES

            question = Question.objects.create(
                form=form,
                text=data.get("text"),
            )

            if "image" in files:
                question.image = files["image"]
                question.save()

            return JsonResponse({"message": "Question added successfully", "question_id": question.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def add_option_to_question(request, question_id):
    if request.method == "POST":
        try:
            question = get_object_or_404(Question, id=question_id)
            data = request.POST
            files = request.FILES

            option = Option.objects.create(
                question=question,
                text=data.get("text"),
                is_correct=data.get("is_correct", False),
            )

            if "image" in files:
                option.image = files["image"]
                option.save()

            return JsonResponse({"message": "Option added successfully", "option_id": option.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def get_course_questions(request, course_id):
    if request.method == "GET":
        try:
            course = Course.objects.get(id=course_id)
            forms = course.forms.all()  # Получаем все формы для курса
            response_data = []

            for form in forms:
                form_data = {
                    "form_id": form.id,
                    "title": form.title,
                    "description": form.description,
                    "image": request.build_absolute_uri(form.image.url) if form.image else None,
                    "questions": []
                }

                for question in form.questions.all():  # Получаем все вопросы для формы
                    question_data = {
                        "id": question.id,
                        "text": question.text,
                        "image": request.build_absolute_uri(question.image.url) if question.image else None,
                        "options": []
                    }

                    for option in question.options.all():  # Получаем все варианты ответов для вопроса
                        option_data = {
                            "id": option.id,
                            "text": option.text,
                            "is_correct": option.is_correct,
                            "image": request.build_absolute_uri(option.image.url) if option.image else None,
                        }
                        question_data["options"].append(option_data)

                    form_data["questions"].append(question_data)

                response_data.append(form_data)

            return JsonResponse({"forms": response_data}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Метод не поддерживается"}, status=405)


@csrf_exempt
def check_answers(request, course_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            user_id = data.get('user_id')
            user = CustomUser.objects.get(id=user_id)

            correct_answers = 0
            total_questions = 0

            course = Course.objects.get(id=course_id)

            answers = data.get('answers', {})
            for question_id, selected_option_id in answers.items():
                question = Question.objects.get(id=question_id)
                total_questions += 1

                # Проверяем, что вопрос принадлежит курсу
                if question.form.course != course:
                    return JsonResponse({"error": f"Question {question_id} does not belong to this course"}, status=400)

                correct_option = question.options.filter(is_correct=True).first()
                if correct_option and correct_option.id == selected_option_id:
                    correct_answers += 1

            # Начисляем опыт пользователю
            user.add_experience(correct_answers)

            # Сохраняем результат теста
            QuizResult.objects.create(
                user=user,
                course=course,
                correct_answers=correct_answers,
            )

            return JsonResponse({
                "correct": correct_answers,
                "total": total_questions,
                "score": f"Всего правильных ответов {correct_answers} из {total_questions} вопросов",
                "level": user.level,  # Возвращаем текущий уровень пользователя
                "experience": user.experience,  # Возвращаем текущий опыт пользователя
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Метод не поддерживается"}, status=405)


@csrf_exempt
def create_achievements(request):

    default_achievements = [
        {
            "title": "Первый курс",
            "description": "Пройдите первый курс, чтобы получить эту ачивку.",
            "condition": "first_course",
        },
        {
            "title": "Топ-1 в рейтинге",
            "description": "Станьте лучшим игроком в рейтинге.",
            "condition": "top_1",
        },
        {
            "title": "Все задачи курса выполнены верно",
            "description": "Выполните все задачи курса с правильными ответами.",
            "condition": "all_correct",
        },
        {
            "title": "Три курса выполнены",
            "description": "Пройдите три курса, чтобы получить эту ачивку.",
            "condition": "three_courses",
        },
    ]

    created_achievements = []
    for achievement_data in default_achievements:
        achievement, created = Achievement.objects.get_or_create(
            condition=achievement_data["condition"],
            defaults={
                "title": achievement_data["title"],
                "description": achievement_data["description"],
            }
        )
        if created:
            created_achievements.append({
                "title": achievement.title,
                "description": achievement.description,
                "condition": achievement.condition,
            })

    return JsonResponse({
        "default_achievements": default_achievements,
        "status": "success",
    })


@csrf_exempt
def user_achievements_view(request, user_id):
    try:
        user = get_object_or_404(CustomUser, id=user_id)

        all_achievements = Achievement.objects.all()

        # Проверяем "Первый курс" (id=1)
        if not UserAchievement.objects.filter(user=user, achievement_id=1).exists():
            if QuizResult.objects.filter(user=user).exists():
                achievement = get_object_or_404(Achievement, id=1)
                UserAchievement.objects.create(user=user, achievement=achievement)

        # Проверяем "Топ-1 в рейтинге" (id=2)
        if not UserAchievement.objects.filter(user=user, achievement_id=2).exists():
            user_total_score = QuizResult.objects.filter(user=user).aggregate(total=Sum('correct_answers'))['total'] or 0
            top_score_user = (
                QuizResult.objects.values('user_id')
                .annotate(total=Sum('correct_answers'))
                .order_by('-total')
                .first()
            )
            if top_score_user and top_score_user['user_id'] == user.id:
                achievement = get_object_or_404(Achievement, id=2)
                UserAchievement.objects.create(user=user, achievement=achievement)

        # Проверяем "Все задачи выполнены верно" (id=3)
        if not UserAchievement.objects.filter(user=user, achievement_id=3).exists():
            courses = QuizResult.objects.filter(user=user).values('course_id').distinct()
            for course in courses:
                total_questions = Question.objects.filter(course_id=course['course_id']).count()
                correct_answers = QuizResult.objects.filter(
                    user=user, course_id=course['course_id']
                ).aggregate(total=Sum('correct_answers'))['total'] or 0
                if total_questions == correct_answers:
                    achievement = get_object_or_404(Achievement, id=3)
                    UserAchievement.objects.create(user=user, achievement=achievement)
                    break

        # Проверяем "Три курса выполнены" (id=4)
        if not UserAchievement.objects.filter(user=user, achievement_id=4).exists():
            completed_courses = Enrollment.objects.filter(user=user).values('course_id').distinct().count()
            if completed_courses >= 3:
                achievement = get_object_or_404(Achievement, id=4)
                UserAchievement.objects.create(user=user, achievement=achievement)

        # Формируем ответ с полученными ачивками
        user_achievements = UserAchievement.objects.filter(user=user).select_related("achievement")
        response_data = [
            {
                "id": ua.achievement.id,
                "title": ua.achievement.title,
                "description": ua.achievement.description,
                "date_earned": ua.date_earned.isoformat(),
            }
            for ua in user_achievements
        ]

        return JsonResponse({"achievements": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@login_required
def edit_course(request, course_id):
    if request.method in ["PUT", "PATCH"]:
        try:
            course = get_object_or_404(Course, id=course_id)

            # Проверяем, что пользователь является автором курса или суперпользователем
            if request.user != course.author and not request.user.is_superuser:
                return JsonResponse({"error": "You do not have permission to edit this course"}, status=403)

            data = json.loads(request.body.decode("utf-8"))

            # Обновляем поля курса, если они переданы в запросе
            if "title" in data:
                course.title = data["title"]
            if "description" in data:
                course.description = data["description"]
            if "tags" in data:
                course.tags = data["tags"]
            if "content" in data:
                course.content = data["content"]

            course.save()

            return JsonResponse({"message": "Course updated successfully"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def get_notifications(request, user_id):
    if request.method == "GET":
        try:
            user = get_object_or_404(CustomUser, id=user_id)
            notifications = user.notifications.order_by("-created_at").values("message", "created_at")
            return JsonResponse({"notifications": list(notifications)}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def get_level_history(request, user_id):
    if request.method == "GET":
        try:
            user = get_object_or_404(CustomUser, id=user_id)
            history = user.level_history.order_by("-achieved_at").values("level", "achieved_at")
            return JsonResponse({"level_history": list(history)}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Method not allowed"}, status=405)
