from django.urls import path
from . import views

urlpatterns = [
    path("api/register/", views.register, name="register"),
    path("api/login/", views.login_view, name="login"),
    path("api/profile/", views.profile_view, name="profile_view"),
    path("api/courses/", views.courses_list, name="courses_list"),
    path("api/course/<int:course_id>/", views.course_detail, name="course_detail"),
    path("api/courses/create/", views.create_course, name="create_course"),
    path(
        "api/courses/<int:course_id>/enroll/", views.enroll_course, name="enroll_course"
    ),
    path(
        "api/user/<int:user_id>/courses/",
        views.user_enrolled_courses,
        name="user_enrolled_courses",
    ),
    path("api/users/<int:user_id>/edit/", views.edit_user, name="edit_user"),
    path("api/delete_user/<int:user_id>/", views.delete_user, name="delete_user"),
    path("api/courses/users", views.count_user_correct_answers, name="count_user_correct_answers"),
    path("api/courses/<int:course_id>/add-form/", views.add_form, name="add_form"),
    path("api/courses/<int:course_id>/questions/", views.get_course_questions, name="get_course_questions"),
    path("api/courses/<int:course_id>/check-answers/", views.check_answers, name="check_answers"),
]
