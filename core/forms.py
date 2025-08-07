from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import (
    Assignment,
    Course,
    CourseMaterial,
    ExamSubmission,
    Grade,
    User,
    UserProfile,
)


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("role",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limite les choix au rôle "student" uniquement
        self.fields["role"].choices = [
            choice for choice in User.ROLE_CHOICES if choice[0] == "student"
        ]
        self.fields["role"].required = True


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["avatar", "bio"]


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description"]


class AssignmentForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
    )

    class Meta:
        model = Assignment
        fields = ["title", "description", "due_date"]


class ExamGenerationForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        label="Select Course",
        help_text="Select the course for which you want to generate an exam.",
    )
    prompt = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
        label="AI Exam Prompt",
        help_text="Provide a detailed description or a list of topics for the exam.",
    )


class ExamSubmissionForm(forms.ModelForm):
    class Meta:
        model = ExamSubmission
        fields = ["answers"]

    def __init__(self, *args, **kwargs):
        self.exam_questions = kwargs.pop("exam_questions", None)
        super().__init__(*args, **kwargs)
        if self.exam_questions:
            for i, question in enumerate(self.exam_questions):
                self.fields[f"question_{i}"] = forms.CharField(
                    label=question.get("question_text", f"Question {i+1}"),
                    widget=forms.TextInput(attrs={"placeholder": "Your answer here"}),
                )

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = [
            "title",
            "description",
            "material_type",
            "file",
            "external_url",
            "is_downloadable",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "placeholder": "Enter material title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "rows": 4,
                    "placeholder": "Enter material description",
                }
            ),
            "material_type": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                }
            ),
            "file": forms.FileInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                }
            ),
            "external_url": forms.URLInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "placeholder": "https://example.com",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")
        external_url = cleaned_data.get("external_url")

        if not file and not external_url:
            raise forms.ValidationError(
                "Please provide either a file or an external URL."
            )

        return cleaned_data


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ["assignment", "student", "score"]
