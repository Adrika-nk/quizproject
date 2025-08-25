from django.urls import include, path
from . import views
app_name = 'quizapp'

urlpatterns = [
    path('',views.home, name='home'),
    # Authentication
    # path("login/", views.login_view, name="login"),
    # path('register/', views.register_view, name='register'),
    # path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('quiz/<int:quiz_id>/', views.attempt_quiz, name='attempt_quiz'),
    path('attempt_quiz/<int:course_id>/', views.attempt_quiz, name='attempt_quiz'),
    path('certificate/', views.certificate_view, name='certificate'),

    path('feedback/<int:quiz_id>/', views.submit_feedback, name='submit_feedback'),
    # path('notes/<int:course_id>/', views.view_notes, name='view_notes'),
    path('view_notes/<int:course_id>/', views.view_notes, name='view_notes'),


    # path("login/", views.login_request, name="login"),
    path("confirm-login/<uidb64>/<token>/", views.confirm_login, name="confirm_login"),
    path("course/<int:course_id>/videos/", views.view_videos, name="view_videos"),
    path("submit-task/<int:task_id>/", views.submit_task, name="submit_task"),
    # Student
    path("student/register/", views.student_register_view, name="student_register"),
    path("student/login/",views.student_login_view, name="student_login"),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),

    # Trainer
    path("trainer/register/", views.trainer_register_view, name="trainer_register"),
    path("trainer/login/",views.trainer_login_view, name="trainer_login"),

    path("trainer/dashboard/", views.trainer_dashboard, name="trainer_dashboard"),

    # Admin approval pending page (for trainer)
    path("pending-approval/", views.pending_approval, name="pending_approval"),

    # path("feedback/", views.feedback_view, name="feedback"),
    # path("feedback/thanks/", views.feedback_thanks_view, name="feedback_thanks"),
    # path('submit_feedback/<int:quiz_id>/', views.submit_feedback, name='submit_feedback'),
    # path('quiz_result/<int:quiz_id>/', views.quiz_result, name='quiz_result'),




]
