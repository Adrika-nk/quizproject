from collections import defaultdict
from datetime import date
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import requests

from .forms import  FeedbackForm, RegisterForm, QuizAnswerForm
from .models import Course, Note,  Quiz, Question, QuizAttempt, Student, Trainer, UpdateUser
from quizapp.models import QuizResult
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .models import Course, Question, QuizResult
from django.template.loader import render_to_string

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core.mail import send_mail
from .models import LoginToken
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from .models import DailyTask, TaskSubmission
from googleapiclient.discovery import build



YOUTUBE_API_KEY = "AIzaSyBA8Oylp1lqUr2bTUBRrRUHPPoQAzkK1aA"


# Create your views here.
# Home Page
# def register_view(request):
#     if request.method == 'POST':
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('quizapp:dashboard')
#     else:
#         form = RegisterForm()
#     return render(request, 'register.html', {'form': form})



def student_register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_student = True
            user.save()
            Student.objects.create(user=user)  # create student profile
            login(request, user)
            return redirect('quizapp:student_dashboard')
    else:
        form = RegisterForm()
    return render(request, 'student_register.html', {'form': form})

def student_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.user:   # ✅ check student flag
                login(request, user)
                return redirect("quizapp:student_dashboard")
            else:
                messages.error(request, "This account is not a student account.")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "student_login.html")

@login_required
def student_dashboard(request):
    return render(request, "student_dashboard.html")


def trainer_register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_trainer = True
            user.is_active = False  # Trainer needs approval
            user.save()
            Trainer.objects.create(user=user)  # create trainer profile
            return redirect('quizapp:pending_approval')
    else:
        form = RegisterForm()
    return render(request, 'trainer_register.html', {'form': form})


def trainer_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        print(user,"saheer")
        if user is not None:
            if user.is_tr:   # ✅ check trainer flag
                # if you also track approval in a Trainer model:
                if hasattr(user, "trainer_profile") and not user:
                    messages.warning(request, "Your account is awaiting admin approval.")
                    return redirect("quizapp:pending_approval")
                login(request, user)
                return redirect("quizapp:trainer_dashboard")
            else:
                messages.error(request, "This account is not a trainer account.")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "trainer_login.html")


def trainer_dashboard(request):
    trainer = request.user.trainer
    if not trainer.is_approved:
        return redirect("quizapp:pending_approval")
    return render(request, "trainer_dashboard.html")

@login_required
def pending_approval(request):
    return render(request, "pending_approval.html")

# Login
# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(username=username, password=password)
#         if user:
#             login(request, user)
#             return redirect('quizapp:dashboard')
#         else:
#             messages.error(request, "Invalid credentials")
#     return render(request, 'login.html')
def home(request):
    
    return render(request, 'home.html')



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user:
            if user.is_trainer and not user.trainer_profile.approved:
                messages.error(request, "Your trainer account is pending approval.")
                return redirect('quizapp:login')

            login(request, user)
            if user.is_student:
                return redirect('quizapp:student_dashboard')
            elif user.is_trainer:
                return redirect('quizapp:trainer_dashboard')
            else:
                return redirect('quizapp:dashboard')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'login.html')


# Register

# Logout
def logout_view(request):
    logout(request)
    return redirect('quizapp:home')

# Dashboard
@login_required
def dashboard(request):
    print("hai")
    courses = Course.objects.all()
    results = QuizResult.objects.filter(user=request.user)
    attempts = []
    for r in results:
        total_marks = getattr(r.quiz, 'total_marks', 100)  # default to 100 if missing
        percent_num = (r.score / total_marks) * 100 if total_marks else 0
        print(r.created_at,"hello")
        if percent_num >= 80:
            css_class = "bg-success"
        elif percent_num >= 50:
            css_class = "bg-warning"
        else:
            css_class = "bg-danger"

        attempts.append({
            "result": r,
            "percent_num": percent_num,  # numeric value for template
            "css": css_class,
            'created_at':r.created_at
        })
    

    # --- Daily Task Logic ---
    today = timezone.localdate()
    todays_tasks = DailyTask.objects.filter(date=today, course__in=courses).select_related('course')

    # attach the current user's submission to each task
    user = request.user if request.user.is_authenticated else None
    for t in todays_tasks:
        t.user_submission = None
        if user and user.is_authenticated:
            t.user_submission = TaskSubmission.objects.filter(task=t, student=user).first()

    # group tasks by course and attach to each course obj
    tasks_map = defaultdict(list)
    for t in todays_tasks:
        tasks_map[t.course_id].append(t)
    for c in courses:
        # c.todays_tasks is now available directly in the template
        setattr(c, 'todays_tasks', tasks_map.get(c.id, []))

    # --- YouTube Search Logic ---
    youtube_results = []
    query = request.GET.get("q")
    if query:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "key": YOUTUBE_API_KEY,
            "maxResults": 6,
            "type": "video"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            youtube_results = data.get("items", [])

    return render(request, "dashboard.html", {
        "courses": courses,
        "attempts": attempts,
        "youtube_results": youtube_results,
        "query": query
    })
# Course Details & Quizzes
@login_required
# def course_detail(request, course_id):
#     course = get_object_or_404(Course, id=course_id)
#     print('hello',course_id)
#     questions = Question.objects.filter(course=course)
#     return render(request, 'course_detail.html', {'course': course, 'questions': questions})


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    questions = Question.objects.filter(course=course)

    # --- Daily Task Logic ---
    today = timezone.now().date()
    # Get today's tasks for this course
    tasks = DailyTask.objects.filter(course=course, date=today)

    # Check if user has already submitted today's task
    user_submission = None
    if request.user.is_authenticated:
        user_submission = TaskSubmission.objects.filter(
            student=request.user, task__in=tasks
        ).first()

    return render(request, 'course_detail.html', {
        'course': course,
        'questions': questions,
        'tasks': tasks,
        'user_submission': user_submission
    })

# Attempt Quiz
# @login_required
# def attempt_quiz(request, quiz_id):
#     print('quiz_id',quiz_id)
#     quiz = get_object_or_404(Quiz, course_id=quiz_id)
#     print('quiz',quiz)
#     course = quiz.course
#     questions = Question.objects.filter(course=course)
#     print("adrika")
#     if request.method == 'POST':
#         score = 0
#         total_questions = questions.count()

#         # ✅ Calculate score
#         for question in questions:
#             selected_option = request.POST.get(f"question_{question.id}")
#             if selected_option and selected_option == question.correct_answer:
#                 score += 1

#         # ✅ Save quiz attempt
#         QuizAttempt.objects.create(
#             user=request.user,
#             quiz=quiz,
#             score=score
#         )

#         # ✅ Determine pass/fail
#         if score >= quiz.pass_mark:
#             status = 'Passed ✅'
#             passed = True
#         else:
#             status = 'Failed ❌'
#             passed = False

#         # ✅ Save quiz result
#         QuizResult.objects.create(
#             user=request.user,
#             course=course,
#             quiz=quiz,
#             score=score
#         )

#         return render(request, 'quiz_result.html', {
#             'score': score,
#             'total': total_questions,
#             'status': status,
#             'passed': passed,  # Pass to template for button logic
#             'quiz_id': quiz.id  # ✅ here
#         })
#     print("adrika")
#     return render(request, 'attempt_quiz.html', {'quiz': quiz, 'questions': questions})



@login_required
def attempt_quiz(request, course_id):
    courseqs = get_object_or_404(Course, id=course_id)
    print("haai",course_id)
    questions = Question.objects.filter(course=courseqs).order_by('id')
    quiz=get_object_or_404(Quiz,course_id=course_id)

    if request.method == 'POST':
        score = 0
        total_questions = questions.count()

        # Create attempt first (score will be updated after tally)
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=0
        )

        incorrect_rows = []  # collect data for the email

        for q in questions:
            selected = request.POST.get(f"question_{q.id}")  # 'a'|'b'|'c'|'d' or None
            is_correct = (selected == q.correct_answer)
            if is_correct:
                score += 1

            # Save per-question answer
            from .models import AttemptAnswer  # local import to avoid circulars
            AttemptAnswer.objects.create(
                attempt=attempt,
                question=q,
                selected_option=selected,
                is_correct=is_correct
            )

            if not is_correct:
                # Text for selected and correct answers
                selected_text = getattr(q, f'option_{selected}') if selected else 'Not answered'
                correct_text = getattr(q, f'option_{q.correct_answer}')
                incorrect_rows.append({
                    "question": q.text,
                    "your_letter": (selected or "-"),
                    "your_text": selected_text,
                    "correct_letter": q.correct_answer,
                    "correct_text": correct_text,
                })

        # Update attempt score
        attempt.score = score
        attempt.save()

        # Save overall result (you already do this)
        QuizResult.objects.create(
            user=request.user,
            course=courseqs,
            quiz=quiz,
            score=score
        )

        # ---- SEND EMAIL ----
        to_email = (request.user.email or "").strip()
        if to_email:  # only send if user has an email
            subject = f"Your quiz result: {courseqs.name}"
            print(courseqs.name,'apple')

            # Plain text fallback
            lines = [
                f"Hi {request.user.username},",
                f"You scored {score}/{total_questions} on '{courseqs.name}'.",
                ""
            ]
            if incorrect_rows:
                lines.append("Incorrect answers:")
                for i, row in enumerate(incorrect_rows, start=1):
                    lines.append(
                        f"{i}. {row['question']}\n"
                        f"   Your answer: {row['your_text']} ({row['your_letter']})\n"
                        f"   Correct: {row['correct_text']} ({row['correct_letter']})"
                    )
            else:
                lines.append("Great job — you answered everything correctly!")
            plain_text = "\n".join(lines)

            # HTML version
            table_rows_html = "".join(
                f"<tr>"
                f"<td>{i}</td>"
                f"<td>{row['question']}</td>"
                f"<td>{row['your_text']} ({row['your_letter']})</td>"
                f"<td>{row['correct_text']} ({row['correct_letter']})</td>"
                f"</tr>"
                for i, row in enumerate(incorrect_rows, start=1)
            )
            html_content = f"""
                <p>Hi {request.user.username},</p>
                <p>You scored <strong>{score}/{total_questions}</strong> on <strong>{courseqs.name}</strong>.</p>
                {
                    f"""
                    <p>Here are the questions you got wrong:</p>
                    <table border="1" cellpadding="6" cellspacing="0">
                        <thead>
                            <tr><th>#</th><th>Question</th><th>Your answer</th><th>Correct answer</th></tr>
                        </thead>
                        <tbody>{table_rows_html}</tbody>
                    </table>
                    """
                    if incorrect_rows else
                    "<p>Great job — you answered everything correctly! 🎉</p>"
                }
                <p>Thanks,<br>Quiz App</p>
            """

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to_email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
        # ---- END EMAIL ----

        # Pass/fail banner (unchanged)
        passed = score >= quiz.pass_mark
        status = 'Passed ✅' if passed else 'Failed ❌'

        return render(request, 'quiz_result.html', {
            'score': score,
            'total': total_questions,
            'status': status,
            'passed': passed,
            'quiz_id': quiz.id
        })

    return render(request, 'attempt_quiz.html', {'quiz': quiz, 'questions': questions})



@login_required
def certificate_view(request):
    latest_result = QuizResult.objects.filter(user=request.user).order_by('-created_at').first()

    if not latest_result or latest_result.score < latest_result.quiz.pass_mark:
        return HttpResponseForbidden("You are not eligible for a certificate.")

    return render(request, 'certificate.html', {
        'username': request.user.username,
        'course': latest_result.course.name,
        'score': latest_result.score,
        'date': latest_result.created_at.date()
    })



def submit_feedback(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.quiz = quiz
            feedback.user = request.user
            feedback.save()
            return redirect('quizapp:dashboard')  # Redirect after submission
    else:
        form = FeedbackForm()

    return render(request, 'feedback_form.html', {'form': form, 'quiz': quiz})



def view_notes(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    # notes = Note.objects.filter(course=course)
    # return render(request, "view_notes.html", {"course": course, "notes": notes})
    return render(request, 'view_notes.html', {'course': course})



def login_request(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Generate token for confirmation
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            confirm_url = request.build_absolute_uri(
                reverse("quizapp:confirm_login", kwargs={"uidb64": uid, "token": token})
            )

            # Send confirmation email
            send_mail(
                "Confirm your login",
                f"Hello {user.username},\n\nClick the link below to confirm your login:\n{confirm_url}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            messages.success(request, "A confirmation email has been sent to your registered email. Please confirm to log in.")
            return redirect("quizapp:login")  # redirect back to login page
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, "login.html")
    

def confirm_login(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UpdateUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        login(request, user)
        messages.success(request, "You have successfully logged in.")
        return redirect("quizapp:dashboard")
    else:
        messages.error(request, "Login confirmation link is invalid or expired.")
        return redirect("quizapp:login")
    


def view_videos(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    videos = course.videos.all()  # thanks to related_name="videos"
    return render(request, "view_videos.html", {"course": course, "videos": videos})



def submit_task(request, task_id):
    task = get_object_or_404(DailyTask, pk=task_id)
    if request.method == "POST":
        answer = (request.POST.get("answer") or "").strip()
        if answer:
            # create or update user's submission for this task
            TaskSubmission.objects.update_or_create(
                task=task,
                student=request.user,
                defaults={'answer': answer, 'status': 'PENDING'}
            )
    return redirect('quizapp:dashboard')





