from datetime import timedelta
import uuid
from django.db import models
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class UpdateUser(AbstractUser):
    
    is_trainer = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    


class Course(models.Model):
    name = models.CharField(max_length=100, default="Untitled Course")
    description = models.TextField()
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)

    def __str__(self):
        return self.name


class Quiz(models.Model):
    course = models.ForeignKey(Course, related_name='quizzes', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    total_marks = models.PositiveIntegerField(default=0)
    pass_mark = models.PositiveIntegerField(default=0)
    class Meta:
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.title


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1, choices=[('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')])

    def __str__(self):
        return self.text


class QuizResult(models.Model):
    user = models.ForeignKey(UpdateUser, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}"


class UserResponse(models.Model):
    user = models.ForeignKey(UpdateUser, on_delete=models.CASCADE)  # Skip if no authentication
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    score = models.IntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)



class QuizAttempt(models.Model):
    user = models.ForeignKey(UpdateUser, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    attempted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}"



class Feedback(models.Model):
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE)
    user = models.ForeignKey(UpdateUser, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=20, choices=[
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ])
    clarity_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1-5 stars
    comments = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.username} for {self.quiz.title}"
    


class AttemptAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(
        max_length=1,
        choices=[('a','A'),('b','B'),('c','C'),('d','D')],
        blank=True, null=True   # allow unanswered
    )
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.attempt.user.username} - Q{self.question.id} - {self.selected_option or 'blank'}"



class Note(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return f"{self.title} - {self.course.name}"
    


class LoginToken(models.Model):
    user = models.ForeignKey(UpdateUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"Login token for {self.user.username}"
    


class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="videos")
    title = models.CharField(max_length=200)
    url = models.URLField()

    def save(self, *args, **kwargs):
        # Automatically convert normal YouTube link into embed format
        if "watch?v=" in self.url:
            self.url = self.url.replace("watch?v=", "embed/")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title




class DailyTask(models.Model):
    course = models.ForeignKey('Course', related_name='daily_tasks', on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    question = models.TextField()

    def __str__(self):
        return f"{self.course.name} - {self.date}"

class TaskSubmission(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("UNDER_REVIEW", "Under Review"),
        ("REVIEWED", "Reviewed"),
    ]
    task = models.ForeignKey(DailyTask, related_name='submissions', on_delete=models.CASCADE)
    student = models.ForeignKey(UpdateUser, related_name='task_submissions', on_delete=models.CASCADE)
    answer = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    class Meta:
        unique_together = ('task', 'student')  # one submission per user per task

    def __str__(self):
        return f"{self.student.username} - {self.task} ({self.get_status_display()})"
    




# class Trainer(models.Model):
#     user = models.OneToOneField(UpdateUser, on_delete=models.CASCADE, limit_choices_to={'role': 'trainer'})
#     courses = models.ManyToManyField('Course')  # Trainer can manage multiple courses
#     is_approved = models.BooleanField(default=False)  # Admin approval

#     def __str__(self):
#         return self.user.username



class Trainer(models.Model):
    user = models.OneToOneField(UpdateUser, on_delete=models.CASCADE, related_name="trainer_profile")
    expertise = models.CharField(max_length=200, blank=True, null=True)
    approved = models.BooleanField(default=False)  # admin must approve trainer

    def __str__(self):
        return f"Trainer: {self.user.username}"


class Student(models.Model):
    user = models.OneToOneField(UpdateUser, on_delete=models.CASCADE, related_name="student_profile")
    enrolled_courses = models.ManyToManyField('Course', blank=True)

    def __str__(self):
        return f"Student: {self.user.username}"