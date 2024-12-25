from django.contrib.auth import authenticate, login, get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from .models import CustomUser, Course, Enrollment, Option, Question, QuizResult
import json
from django.contrib.auth.decorators import login_required
from django.db.models import Sum


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
def add_form(request, course_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            course = Course.objects.get(id=course_id)

            for question_data in data["questions"]:
                question = Question.objects.create(course=course, text=question_data["text"])

                for option_data in question_data["options"]:
                    Option.objects.create(
                        question=question,
                        text=option_data["text"],
                        is_correct=option_data["is_correct"]
                    )
            return JsonResponse({"message": "Форма успешно добавлена!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Метод не поддерживается"}, status=405)


def get_course_questions(request, course_id):
    if request.method == "GET":
        try:
            course = Course.objects.get(id=course_id)
            questions = course.questions.all()
            response_data = []

            for question in questions:
                options = question.options.all()
                response_data.append({
                    'id': question.id,
                    'text': question.text,
                    'options': [{'id': option.id, 'text': option.text} for option in options],
                })

            return JsonResponse({"questions": response_data})
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

                correct_option = question.options.filter(is_correct=True).first()
                if correct_option and correct_option.id == selected_option_id:
                    correct_answers += 1

            QuizResult.objects.create(
                user=user,
                course=course,
                correct_answers=correct_answers,
            )

            return JsonResponse({
                "correct": correct_answers,
                "total": total_questions,
                "score": f"Всего правильных ответов {correct_answers} из {total_questions} вопросов"
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Метод не поддерживается"}, status=405)

