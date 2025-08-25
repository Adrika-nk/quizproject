from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Course, Feedback,  Quiz, Question, UpdateUser
from django import forms


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = UpdateUser
        fields = ['username', 'email', 'password1', 'password2']

        def save(self, commit=True):
            user = super().save(commit=False)
            user.email = self.cleaned_data["email"]
            if commit:
                user.save()
            return user
        

class QuizAnswerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super(QuizAnswerForm, self).__init__(*args, **kwargs)
        for question in questions:
            self.fields[str(question.id)] = forms.ChoiceField(
                label=question.question_text,
                choices=[
                    ('A', question.option_a),
                    ('B', question.option_b),
                    ('C', question.option_c),
                    ('D', question.option_d)
                ],
                widget=forms.RadioSelect,
                required=True
            )

class QuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super(QuizForm, self).__init__(*args, **kwargs)
        for question in questions:
            self.fields[f"question_{question.id}"] = forms.ChoiceField(
                label=question.text,
                choices=[
                    ('a', question.option_a),
                    ('b', question.option_b),
                    ('c', question.option_c),
                    ('d', question.option_d),
                ],
                widget=forms.RadioSelect
            )






# class FeedbackForm(forms.ModelForm):
#     class Meta:
#         model = Feedback
#         fields = ['rating', 'comment']
#         widgets = {
#             'rating': forms.Select(attrs={'class': 'form-select'}),
#             'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#         }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['difficulty', 'clarity_rating', 'comments']