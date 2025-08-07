# Fichier : core/views.py

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Importez ce formulaire pour la vue de connexion
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

# API ViewSets
from rest_framework import permissions, viewsets

from .ai.gemini import (
    explain_concept,
    generate_assignment_rubric,
    generate_course_syllabus,
    generate_exam_content,
    generate_lesson_plan,
    generate_quiz_questions,
)
from .forms import (
    AssignmentForm,
    CourseForm,
    CourseMaterialForm,
    CustomUserCreationForm,
    UserProfileForm,
)
from .models import (
    Announcement,
    Assignment,
    AssignmentSubmission,
    CalendarEvent,
    Choice,
    Course,
    CourseCategory,
    CourseMaterial,
    Discussion,
    DiscussionPost,
    Enrollment,
    Exam,
    ExamSubmission,
    Grade,
    Notification,
    Question,
    StudentProgress,
    User,
    UserProfile,
)
from .serializers import (
    AssignmentSerializer,
    CourseSerializer,
    EnrollmentSerializer,
    GradeSerializer,
)


class IsInstructor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "instructor"


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [
                permissions.IsAdminUser | (permissions.IsAuthenticated and IsInstructor)
            ]
        return super().get_permissions()


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]


from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Importez ce formulaire pour la vue de connexion
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .ai.gemini import (
    explain_concept,
    generate_assignment_rubric,
    generate_course_syllabus,
    generate_exam_content,
    generate_lesson_plan,
    generate_quiz_questions,
)
from .forms import AssignmentForm, CourseForm, CustomUserCreationForm, UserProfileForm
from .models import (
    Announcement,
    Assignment,
    AssignmentSubmission,
    CalendarEvent,
    Choice,
    Course,
    CourseCategory,
    CourseMaterial,
    Discussion,
    DiscussionPost,
    Enrollment,
    Exam,
    ExamSubmission,
    Grade,
    Notification,
    Question,
    StudentProgress,
    User,
    UserProfile,
)


def home_view(request):
    return render(request, "core/home.html")


def register_view(request):
    if request.method == "POST":
        user_form = CustomUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, "Account created successfully!")
            return redirect("login")
    else:
        user_form = CustomUserCreationForm()
        profile_form = UserProfileForm()
    return render(
        request,
        "core/register.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    # Le contexte est mis à jour pour passer le formulaire à la template
    return render(request, "core/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard_redirect(request):
    role = getattr(request.user, "role", None)
    if role == "admin":
        return redirect("admin_dashboard")
    elif role == "instructor":
        return redirect("instructor_dashboard")
    elif role == "student":
        return redirect("student_dashboard")
    return redirect("unauthorized")


class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/modern_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add admin-specific context data
        context.update(
            {
                "total_users": User.objects.count(),
                "total_courses": Course.objects.count(),
                "total_enrollments": Enrollment.objects.count(),
            }
        )
        return context


class InstructorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/modern_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add instructor-specific context data
        user = self.request.user
        my_courses = Course.objects.filter(instructor=user)

        context.update(
            {
                "my_courses_count": my_courses.count(),
                "my_courses": my_courses[:6],  # Show first 6 courses
                "total_students": Enrollment.objects.filter(
                    course__instructor=user
                ).count(),
                "pending_reviews": ExamSubmission.objects.filter(
                    exam__course__instructor=user, graded_at__isnull=True
                ).count(),
                "recent_submissions": ExamSubmission.objects.filter(
                    exam__course__instructor=user
                ).order_by("-submitted_at")[
                    :5
                ],  # Recent 5 submissions
            }
        )
        return context


class StudentDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/modern_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add student-specific context data
        user = self.request.user
        enrollments = Enrollment.objects.filter(student=user)

        # Calculate completed assignments
        completed_assignments = ExamSubmission.objects.filter(student=user).count()

        # Calculate average grade
        submissions = ExamSubmission.objects.filter(student=user, grade__isnull=False)
        avg_grade = submissions.aggregate(models.Avg("grade"))["grade__avg"] or 0

        context.update(
            {
                "enrolled_courses_count": enrollments.count(),
                "completed_assignments": completed_assignments,
                "average_grade": f"{avg_grade:.1f}%" if avg_grade else "N/A",
                "course_completion": 75,  # Placeholder - calculate based on actual progress
                "assignment_completion": 60,  # Placeholder - calculate based on actual progress
            }
        )
        return context


class UnauthorizedView(TemplateView):
    template_name = "core/unauthorized.html"


@login_required
def student_profile_view(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("student_profile")
    else:
        form = UserProfileForm(instance=profile)
    return render(request, "core/student_profile.html", {"form": form})


@login_required
def student_quiz_list(request):
    enrolled_courses = request.user.enrollments.all()
    quizzes = []
    for enrollment in enrolled_courses:
        for exam in enrollment.course.exams.all():
            exam.is_completed_by_user = exam.submissions.filter(
                student=request.user
            ).exists()
            quizzes.append(exam)
    return render(request, "core/student_quiz_list.html", {"quizzes": quizzes})


@login_required
def student_quiz_detail(request, exam_pk):
    exam = get_object_or_404(Exam, pk=exam_pk)

    # Check if student has already submitted
    existing_submission = ExamSubmission.objects.filter(
        exam=exam, student=request.user
    ).first()
    if existing_submission:
        messages.info(request, "You have already submitted this quiz.")
        return redirect("student_quiz_list")

    if request.method == "POST":
        # Collect answers from form
        answers = {}
        for question in exam.questions.all():
            question_key = f"question_{question.id}"
            if question_key in request.POST:
                answer_value = request.POST.get(question_key)
                if question.question_type == "multiple_choice":
                    # For multiple choice, store the choice ID
                    try:
                        choice = question.choices.get(id=answer_value)
                        answers[str(question.id)] = {
                            "answer": answer_value,
                            "choice_text": choice.text,
                            "is_correct": choice.is_correct,
                        }
                    except:
                        answers[str(question.id)] = {"answer": answer_value}
                else:
                    # For true/false and short answer
                    answers[str(question.id)] = {"answer": answer_value}

        # Calculate basic score for multiple choice questions
        total_questions = exam.questions.count()
        correct_answers = 0

        for question_id, answer_data in answers.items():
            if answer_data.get("is_correct"):
                correct_answers += 1

        grade = (correct_answers / total_questions * 100) if total_questions > 0 else 0

        ExamSubmission.objects.create(
            exam=exam, student=request.user, answers=answers, grade=grade
        )
        messages.success(
            request, f"Quiz submitted successfully! Your score: {grade:.1f}%"
        )
        return redirect("student_quiz_list")

    return render(request, "core/student_quiz_detail.html", {"exam": exam})


@login_required
def message_instructor(request, instructor_id):
    instructor = get_object_or_404(User, pk=instructor_id, role="instructor")
    if request.method == "POST":
        message_content = request.POST.get("message")
        # Simulate sending a message (store or send notification)
        messages.success(
            request, f"Message sent to {instructor.first_name} {instructor.last_name}."
        )
        return redirect("student_dashboard")
    return render(request, "core/message_instructor.html", {"instructor": instructor})


@login_required
def profile_update_view(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile_update")
    else:
        form = UserProfileForm(instance=profile)
    return render(request, "core/profile_update.html", {"form": form})


@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, "core/course_list.html", {"courses": courses})


class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "core/course_form.html"
    success_url = reverse_lazy("course_list")

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        return super().form_valid(form)


@login_required
def enroll_in_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user, course=course
    )

    if created:
        messages.success(request, f"Successfully enrolled in {course.title}!")
    else:
        messages.info(request, f"You are already enrolled in {course.title}.")

    # Redirect to course detail page to show course content
    return redirect("course_detail", pk=course.pk)


@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)

    # Check if current user is enrolled
    is_enrolled = False
    if request.user.is_authenticated and request.user.role == "student":
        from core.models import Enrollment

        is_enrolled = Enrollment.objects.filter(
            student=request.user, course=course
        ).exists()

    return render(
        request,
        "core/course_detail.html",
        {"course": course, "is_enrolled": is_enrolled},
    )


@login_required
def assignment_create(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.save()
            return redirect("course_detail", pk=course.pk)
    else:
        form = AssignmentForm()
    return render(
        request, "core/assignment_form.html", {"form": form, "course": course}
    )


@login_required
def generate_exam_view(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if request.method == "POST":
        title = request.POST.get("title")
        instructions = request.POST.get("instructions")
        content = generate_exam_content(title, instructions)
        Exam.objects.create(
            title=title,
            instructions=instructions,
            generated_content=content,
            course=course,
            created_by=request.user,
        )
        messages.success(request, "Exam generated successfully.")
        return redirect("instructor_dashboard")
    return render(request, "core/generate_exam.html", {"course": course})


@login_required
def generate_content_view(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if request.method == "POST":
        prompt = request.POST.get("prompt")
        content = generate_exam_content(prompt)
        messages.success(request, "Content generated successfully.")
        return render(request, "core/generated_content.html", {"content": content})
    return render(request, "core/generate_content.html", {"course": course})


@login_required
def submit_exam_view(request, exam_pk):
    exam = get_object_or_404(Exam, pk=exam_pk)
    if request.method == "POST":
        answers = request.POST.get("answers")
        ExamSubmission.objects.create(exam=exam, student=request.user, answers=answers)
        messages.success(request, "Exam submitted successfully.")
        return redirect("student_dashboard")
    return render(request, "core/exam_submit.html", {"exam": exam})


@login_required
def instructor_exam_submissions(request):
    exams = Exam.objects.filter(created_by=request.user)
    return render(request, "core/instructor_submissions.html", {"exams": exams})


@login_required
def review_submission(request, submission_pk):
    submission = get_object_or_404(ExamSubmission, pk=submission_pk)
    if request.method == "POST":
        submission.feedback = request.POST.get("feedback")
        submission.grade = request.POST.get("grade")
        submission.save()
        messages.success(request, "Submission reviewed.")
        return redirect("instructor_exam_submissions")
    return render(request, "core/review_submission.html", {"submission": submission})


# ======================
# AI-POWERED INSTRUCTOR VIEWS
# ======================


@login_required
def ai_lesson_planner(request):
    """Generate lesson plans using Gemini AI"""
    if request.user.role != "instructor":
        return redirect("unauthorized")

    if request.method == "POST":
        topic = request.POST.get("topic")
        duration = request.POST.get("duration")
        difficulty = request.POST.get("difficulty")

        lesson_plan = generate_lesson_plan(topic, duration, difficulty)

        # Check if we got an error response and use fallback if needed
        if "error" in lesson_plan:
            if lesson_plan.get("quota_exceeded") or lesson_plan.get("rate_limited"):
                from core.ai.gemini import get_fallback_lesson_plan

                lesson_plan = get_fallback_lesson_plan(topic, duration, difficulty)
                if lesson_plan.get("is_demo"):
                    messages.warning(
                        request, "API quota exceeded. Showing demo content."
                    )

        return render(
            request,
            "core/ai_lesson_result.html",
            {"lesson_plan": lesson_plan, "type": "lesson_plan"},
        )

    return render(request, "core/ai_lesson_planner.html")


@login_required
def ai_quiz_generator(request):
    """Generate quiz questions using Gemini AI"""
    if request.user.role != "instructor":
        return redirect("unauthorized")

    if request.method == "POST":
        topic = request.POST.get("topic")
        num_questions = int(request.POST.get("num_questions", 5))
        question_type = request.POST.get("question_type")

        try:
            quiz = generate_quiz_questions(topic, num_questions, question_type)

            # Debug: Check what we got from AI
            print(f"Quiz generated: {quiz}")

            if "error" in quiz:
                # Handle different types of errors
                if quiz.get("quota_exceeded") or quiz.get("rate_limited"):
                    # Use fallback mock data instead of showing error
                    from core.ai.gemini import get_fallback_quiz_data

                    quiz = get_fallback_quiz_data(topic, num_questions, question_type)

                    # Show warning message about using demo content
                    if quiz.get("quota_exceeded"):
                        retry_after = quiz.get("retry_after", 60)
                        messages.warning(
                            request,
                            f"API quota exceeded. Showing demo content. Wait {retry_after} seconds for AI generation or upgrade your Gemini API plan.",
                        )
                    else:
                        messages.warning(
                            request,
                            "Rate limit reached. Showing demo content. Please wait before trying AI generation again.",
                        )
                else:
                    messages.error(request, f"Error generating quiz: {quiz['error']}")

                    # Add context about quota limits
                    context = {
                        "quota_error": quiz.get("quota_exceeded", False),
                        "rate_limited": quiz.get("rate_limited", False),
                        "retry_after": quiz.get("retry_after"),
                        "error_details": quiz.get("details"),
                    }
                    return render(request, "core/ai_quiz_generator.html", context)

            # Store quiz data in session for potential saving
            request.session["generated_quiz"] = quiz

            return render(
                request,
                "core/ai_lesson_result.html",
                {"quiz": quiz, "type": "quiz", "show_save_button": True},
            )

        except Exception as e:
            messages.error(request, f"Unexpected error: {str(e)}")
            return render(request, "core/ai_quiz_generator.html")

    return render(request, "core/ai_quiz_generator.html")


@login_required
def ai_rubric_generator(request):
    """Generate assignment rubrics using Gemini AI"""
    if request.user.role != "instructor":
        return redirect("unauthorized")

    if request.method == "POST":
        assignment_desc = request.POST.get("assignment_description")
        criteria = request.POST.get("grading_criteria")

        rubric = generate_assignment_rubric(assignment_desc, criteria)

        # Check for errors and use fallback if needed
        if isinstance(rubric, dict) and rubric.get("error"):
            if rubric.get("quota_exceeded") or rubric.get("rate_limited"):
                from core.ai.gemini import get_fallback_rubric

                rubric = get_fallback_rubric(assignment_desc, criteria)
                messages.warning(request, "API quota exceeded. Showing demo content.")

        return render(
            request, "core/ai_lesson_result.html", {"rubric": rubric, "type": "rubric"}
        )

    return render(request, "core/ai_rubric_generator.html")


@login_required
def ai_concept_explainer(request):
    """Explain concepts using Gemini AI"""
    if request.user.role != "instructor":
        return redirect("unauthorized")

    if request.method == "POST":
        concept = request.POST.get("concept")
        grade_level = request.POST.get("grade_level")

        explanation = explain_concept(concept, grade_level)

        # Check for errors and use fallback if needed
        if isinstance(explanation, dict) and explanation.get("error"):
            if explanation.get("quota_exceeded") or explanation.get("rate_limited"):
                from core.ai.gemini import get_fallback_explanation

                explanation = get_fallback_explanation(concept, grade_level)
                messages.warning(request, "API quota exceeded. Showing demo content.")

        return render(
            request,
            "core/ai_lesson_result.html",
            {"explanation": explanation, "concept": concept, "type": "explanation"},
        )

    return render(request, "core/ai_concept_explainer.html")


@login_required
def ai_syllabus_generator(request):
    """Generate course syllabus using Gemini AI"""
    if request.user.role != "instructor":
        return redirect("unauthorized")

    if request.method == "POST":
        course_title = request.POST.get("course_title")
        duration = request.POST.get("duration")
        topics = request.POST.get("topics")

        syllabus = generate_course_syllabus(course_title, duration, topics)

        # Check for errors and use fallback if needed
        if isinstance(syllabus, dict) and syllabus.get("error"):
            if syllabus.get("quota_exceeded") or syllabus.get("rate_limited"):
                from core.ai.gemini import get_fallback_syllabus

                syllabus = get_fallback_syllabus(course_title, duration, topics)
                messages.warning(request, "API quota exceeded. Showing demo content.")

        return render(
            request,
            "core/ai_lesson_result.html",
            {"syllabus": syllabus, "course_title": course_title, "type": "syllabus"},
        )

    return render(request, "core/ai_syllabus_generator.html")


@login_required
def create_quiz_from_ai(request):
    """Create and save a quiz from AI-generated content to database"""
    if request.user.role != "instructor":
        return redirect("unauthorized")

    if request.method == "POST":
        # Get the AI-generated quiz data
        topic = request.POST.get("topic")
        quiz_data = request.session.get("generated_quiz")
        course_id = request.POST.get("course_id")

        if not quiz_data or not course_id:
            messages.error(request, "Missing quiz data or course selection.")
            return redirect("ai_quiz_generator")

        try:
            course = Course.objects.get(id=course_id, instructor=request.user)

            # Create the exam
            exam = Exam.objects.create(
                title=f"Quiz: {topic}",
                course=course,
                created_by=request.user,
                instructions="AI-generated quiz. Please answer all questions.",
                generated_content=quiz_data.get("questions", ""),
                time_limit=60,
            )

            # Create questions from parsed data
            if "parsed_questions" in quiz_data:
                for q_data in quiz_data["parsed_questions"]:
                    question = Question.objects.create(
                        exam=exam,
                        text=q_data["text"],
                        question_type=q_data["type"],
                        order=q_data["order"],
                    )

                    # Create choices for multiple choice questions
                    if q_data["type"] == "multiple_choice" and "choices" in q_data:
                        for i, choice_data in enumerate(q_data["choices"]):
                            Choice.objects.create(
                                question=question,
                                text=choice_data["text"],
                                is_correct=(
                                    choice_data["letter"]
                                    == q_data.get("correct_answer")
                                ),
                                order=i,
                            )

            messages.success(request, f"Quiz '{exam.title}' created successfully!")
            return redirect("course_detail", pk=course.id)

        except Course.DoesNotExist:
            messages.error(request, "Course not found or you don't have permission.")
        except Exception as e:
            messages.error(request, f"Error creating quiz: {str(e)}")

    # Show form to select course
    courses = Course.objects.filter(instructor=request.user)
    quiz_data = request.session.get("generated_quiz")

    return render(
        request,
        "core/create_quiz_from_ai.html",
        {"courses": courses, "quiz_data": quiz_data},
    )


@login_required
def ai_dashboard(request):
    """Main AI dashboard for instructors"""
    if request.user.role != "instructor":
        return redirect("unauthorized")

    return render(request, "core/ai_dashboard.html")


@login_required
def assignment_list(request):
    """List assignments for the current user"""
    assignments = Assignment.objects.all()
    return render(request, "core/assignment_list.html", {"assignments": assignments})


@login_required
def exam_submission_list(request):
    """List exam submissions for students"""
    submissions = ExamSubmission.objects.filter(student=request.user)
    return render(
        request, "core/exam_submission_list.html", {"submissions": submissions}
    )


# ======================
# MOODLE-LIKE FEATURES
# ======================


@login_required
def course_categories_view(request):
    """Display course categories hierarchically"""
    categories = CourseCategory.objects.filter(parent=None)  # Root categories
    return render(request, "core/course_categories.html", {"categories": categories})


@login_required
def category_courses_view(request, category_id):
    """Display courses in a specific category"""
    category = get_object_or_404(CourseCategory, id=category_id)
    courses = Course.objects.filter(category=category, is_published=True)
    return render(
        request,
        "core/category_courses.html",
        {"category": category, "courses": courses},
    )


@login_required
def course_materials_view(request, course_id):
    """Display course materials/resources"""
    course = get_object_or_404(Course, id=course_id)
    materials = CourseMaterial.objects.filter(course=course)
    return render(
        request,
        "core/course_materials.html",
        {"course": course, "materials": materials},
    )


@login_required
def access_material(request, material_id):
    """Access a specific course material - redirect to file or external URL"""
    material = get_object_or_404(CourseMaterial, id=material_id)

    # Check if user is enrolled in the course or is the instructor
    is_enrolled = Enrollment.objects.filter(
        student=request.user, course=material.course
    ).exists()
    is_instructor = material.course.instructor == request.user

    if not (is_enrolled or is_instructor):
        messages.error(
            request, "You must be enrolled in this course to access materials."
        )
        return redirect("course_detail", pk=material.course.id)

    # If it's an external URL, redirect to it
    if material.external_url:
        return redirect(material.external_url)

    # If it's a file, serve it or redirect to the file URL
    elif material.file:
        from django.http import HttpResponseRedirect

        return HttpResponseRedirect(material.file.url)

    else:
        messages.error(request, "This material doesn't have an accessible resource.")
        return redirect("course_detail", pk=material.course.id)


@login_required
def course_discussions_view(request, course_id):
    """Display course discussion forums"""
    course = get_object_or_404(Course, id=course_id)
    discussions = Discussion.objects.filter(course=course)
    return render(
        request,
        "core/course_discussions.html",
        {"course": course, "discussions": discussions},
    )


@login_required
def discussion_detail_view(request, discussion_id):
    """Display discussion detail with posts and replies"""
    discussion = get_object_or_404(Discussion, id=discussion_id)
    posts = DiscussionPost.objects.filter(discussion=discussion, parent=None)

    if request.method == "POST":
        content = request.POST.get("content")
        parent_id = request.POST.get("parent_id")

        parent = None
        if parent_id:
            parent = get_object_or_404(DiscussionPost, id=parent_id)

        DiscussionPost.objects.create(
            discussion=discussion, author=request.user, content=content, parent=parent
        )
        messages.success(request, "Post added successfully!")
        return redirect("discussion_detail", discussion_id=discussion.id)

    return render(
        request,
        "core/discussion_detail.html",
        {"discussion": discussion, "posts": posts},
    )


@login_required
def course_announcements_view(request, course_id):
    """Display course announcements"""
    course = get_object_or_404(Course, id=course_id)
    announcements = Announcement.objects.filter(course=course)
    return render(
        request,
        "core/course_announcements.html",
        {"course": course, "announcements": announcements},
    )


@login_required
def student_progress_view(request, course_id=None):
    """Display student progress for specific course or all courses"""
    if course_id:
        course = get_object_or_404(Course, id=course_id)
        progress = StudentProgress.objects.filter(
            student=request.user, course=course
        ).first()
        if not progress:
            progress = StudentProgress.objects.create(
                student=request.user, course=course
            )
        return render(
            request,
            "core/student_course_progress.html",
            {"course": course, "progress": progress},
        )
    else:
        # Show progress for all enrolled courses
        enrollments = Enrollment.objects.filter(student=request.user)
        progress_data = []
        for enrollment in enrollments:
            progress, created = StudentProgress.objects.get_or_create(
                student=request.user, course=enrollment.course
            )
            progress_data.append({"course": enrollment.course, "progress": progress})
        return render(
            request,
            "core/student_progress_overview.html",
            {"progress_data": progress_data},
        )


@login_required
def calendar_view(request):
    """Display calendar with events"""
    # Get events for enrolled courses or instructor's courses
    if request.user.role == "student":
        enrolled_courses = [
            e.course for e in Enrollment.objects.filter(student=request.user)
        ]
        events = CalendarEvent.objects.filter(course__in=enrolled_courses)
    elif request.user.role == "instructor":
        instructor_courses = Course.objects.filter(instructor=request.user)
        events = CalendarEvent.objects.filter(course__in=instructor_courses)
    else:
        events = CalendarEvent.objects.all()

    return render(request, "core/calendar.html", {"events": events})


@login_required
def notifications_view(request):
    """Display user notifications"""
    notifications = Notification.objects.filter(recipient=request.user)
    unread_count = notifications.filter(is_read=False).count()

    # Mark as read when viewing
    if request.GET.get("mark_read"):
        notifications.filter(is_read=False).update(is_read=True)
        return redirect("notifications")

    return render(
        request,
        "core/notifications.html",
        {"notifications": notifications, "unread_count": unread_count},
    )


@login_required
def gradebook_view(request, course_id):
    """Display gradebook for instructors"""
    if request.user.role != "instructor":
        return redirect("unauthorized")

    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    enrollments = Enrollment.objects.filter(course=course)
    assignments = Assignment.objects.filter(course=course)
    exams = Exam.objects.filter(course=course)

    # Create gradebook data structure
    gradebook_data = []
    for enrollment in enrollments:
        student_data = {
            "student": enrollment.student,
            "assignment_grades": {},
            "exam_grades": {},
            "overall_grade": 0,
        }

        # Get assignment submissions
        for assignment in assignments:
            submission = AssignmentSubmission.objects.filter(
                assignment=assignment, student=enrollment.student
            ).first()
            student_data["assignment_grades"][assignment.id] = (
                submission.grade if submission else None
            )

        # Get exam submissions
        for exam in exams:
            submission = ExamSubmission.objects.filter(
                exam=exam, student=enrollment.student
            ).first()
            student_data["exam_grades"][exam.id] = (
                submission.grade if submission else None
            )

        gradebook_data.append(student_data)

    return render(
        request,
        "core/gradebook.html",
        {
            "course": course,
            "assignments": assignments,
            "exams": exams,
            "gradebook_data": gradebook_data,
        },
    )


@login_required
def assignment_submission_view(request, assignment_id):
    """Handle assignment submissions"""
    assignment = get_object_or_404(Assignment, id=assignment_id)

    # Check if student is enrolled in the course
    if not Enrollment.objects.filter(
        student=request.user, course=assignment.course
    ).exists():
        messages.error(request, "You are not enrolled in this course.")
        return redirect("course_list")

    # Get existing submission if any
    submission = AssignmentSubmission.objects.filter(
        assignment=assignment, student=request.user
    ).first()

    if request.method == "POST":
        content = request.POST.get("content", "")
        file = request.FILES.get("file")

        if submission:
            # Update existing submission
            submission.content = content
            if file:
                submission.file = file
            submission.save()
            messages.success(request, "Assignment updated successfully!")
        else:
            # Create new submission
            AssignmentSubmission.objects.create(
                assignment=assignment, student=request.user, content=content, file=file
            )
            messages.success(request, "Assignment submitted successfully!")

        return redirect("course_detail", pk=assignment.course.id)

    return render(
        request,
        "core/assignment_submission.html",
        {"assignment": assignment, "submission": submission},
    )


@login_required
def analytics_dashboard_view(request):
    """Display analytics dashboard for instructors and admins"""
    if request.user.role not in ["instructor", "admin"]:
        return redirect("unauthorized")

    context = {}

    if request.user.role == "instructor":
        # Instructor analytics
        my_courses = Course.objects.filter(instructor=request.user)
        context.update(
            {
                "total_courses": my_courses.count(),
                "total_students": Enrollment.objects.filter(
                    course__instructor=request.user
                ).count(),
                "pending_submissions": AssignmentSubmission.objects.filter(
                    assignment__course__instructor=request.user, grade__isnull=True
                ).count(),
                "recent_submissions": ExamSubmission.objects.filter(
                    exam__course__instructor=request.user
                ).order_by("-submitted_at")[:10],
            }
        )

    elif request.user.role == "admin":
        # Admin analytics
        context.update(
            {
                "total_users": User.objects.count(),
                "total_courses": Course.objects.count(),
                "total_enrollments": Enrollment.objects.count(),
                "recent_enrollments": Enrollment.objects.order_by("-enrolled_at")[:10],
            }
        )

    return render(request, "core/analytics_dashboard.html", context)


# ======================
# COURSE CONTENT MANAGEMENT
# ======================


@login_required
def manage_course_content(request, course_id):
    """Manage course content - view and add materials"""
    course = get_object_or_404(Course, id=course_id)

    # Check if user is the instructor of this course
    if request.user != course.instructor and request.user.role != "admin":
        messages.error(request, "You don't have permission to manage this course.")
        return redirect("course_detail", pk=course.id)

    if request.method == "POST":
        form = CourseMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.save()
            messages.success(
                request, f"Material '{material.title}' added successfully!"
            )
            return redirect("manage_course_content", course_id=course.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CourseMaterialForm()

    return render(
        request, "core/manage_course_content.html", {"course": course, "form": form}
    )


@login_required
def remove_course_content(request, course_id, material_id):
    """Remove a course material"""
    course = get_object_or_404(Course, id=course_id)
    material = get_object_or_404(CourseMaterial, id=material_id, course=course)

    # Check if user is the instructor of this course
    if request.user != course.instructor and request.user.role != "admin":
        messages.error(request, "You don't have permission to manage this course.")
        return redirect("course_detail", pk=course.id)

    if request.method == "POST":
        material_title = material.title
        # Delete the file if it exists
        if material.file:
            try:
                material.file.delete()
            except:
                pass  # File might already be deleted

        material.delete()
        messages.success(request, f"Material '{material_title}' removed successfully!")

    return redirect("manage_course_content", course_id=course.id)  
