from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Course, Note, Quiz, Question, QuizResult, Feedback, Student, TaskSubmissions, Trainer, UpdateUser, Video


# Register your models here.
# class UpdateUserAdmin(UserAdmin):
#     list_display = ('username', 'email', 'is_trainer', 'is_student', 'is_active')

admin.site.register(UpdateUser)
admin.site.register(Trainer)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(QuizResult)
admin.site.register(Feedback)
admin.site.register(Note)
admin.site.register(Video)




# @admin.register(Feedback)
# class FeedbackAdmin(admin.ModelAdmin):
#     list_display = ('user', 'rating', 'comment', 'created_at')
#     readonly_fields = ('created_at',)
#     list_filter = ('rating', 'created_at')


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'user', 'difficulty', 'clarity_rating', 'submitted_at')
    list_filter = ('difficulty', 'clarity_rating', 'submitted_at')
    search_fields = ('user__username', 'quiz__title', 'comments')



# @admin.register(Question)
# class QuestionAdmin(admin.ModelAdmin):
#     list_filter = ('course',)       # ✅ adds filter sidebar
#     list_display = ('text', 'course')  # show question text & course in list

# @admin.register(Course)
# class CourseAdmin(admin.ModelAdmin):
#     list_display = ('name',)  # optional: shows course name in list

# admin.site.register(QuestionAdmin)

# @admin.register(DailyTask)
# class DailyTaskAdmin(admin.ModelAdmin):
#     list_display = ('course', 'date', 'short_q')
#     list_filter = ('course', 'date')

#     def short_q(self, obj):
#         return (obj.question[:60] + '…') if len(obj.question) > 60 else obj.question
#     short_q.short_description = 'Question'

# @admin.register(Course)
# class CourseAdmin(admin.ModelAdmin):
#     list_display = ("title", "trainer")


# @admin.register(Task)
# class TaskAdmin(admin.ModelAdmin):
#     list_display = ("question", "course", "trainer", "created_at")
#     list_filter = ("course", "trainer")


# class TaskSubmissionAdmin(admin.ModelAdmin):
#     list_display = ("task", "student", "status", "submitted_at","answer")
#     list_filter = ("status", "task")

