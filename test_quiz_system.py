#!/usr/bin/env python
"""
Test script for the quiz system functionality
"""
import os
import sys

import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms_backend.settings")
django.setup()

from core.ai.gemini import generate_quiz_questions
from core.models import Choice, Course, Exam, Question, User


def test_quiz_generation():
    """Test the AI quiz generation functionality"""
    print("🧪 Testing AI Quiz Generation...")

    try:
        # Test AI quiz generation
        quiz_data = generate_quiz_questions(
            topic="Python Programming Basics",
            num_questions=3,
            question_type="multiple_choice",
        )

        print(f"✅ Quiz generated successfully!")
        print(f"📝 Topic: {quiz_data.get('topic')}")
        print(f"🔢 Number of questions: {quiz_data.get('num_questions')}")

        if "parsed_questions" in quiz_data:
            print(f"📋 Parsed questions: {len(quiz_data['parsed_questions'])}")
            for i, q in enumerate(quiz_data["parsed_questions"][:2]):  # Show first 2
                print(f"   Q{i+1}: {q.get('text', 'N/A')[:60]}...")

        return quiz_data

    except Exception as e:
        print(f"❌ Quiz generation failed: {e}")
        return None


def test_database_operations():
    """Test database operations for quiz system"""
    print("\n🗄️ Testing Database Operations...")

    try:
        # Check if we have users
        instructors = User.objects.filter(role="instructor")
        students = User.objects.filter(role="student")

        print(f"👨‍🏫 Instructors: {instructors.count()}")
        print(f"👨‍🎓 Students: {students.count()}")

        # Check courses
        courses = Course.objects.all()
        print(f"📚 Courses: {courses.count()}")

        # Check exams
        exams = Exam.objects.all()
        print(f"📝 Exams: {exams.count()}")

        # Check questions
        questions = Question.objects.all()
        print(f"❓ Questions: {questions.count()}")

        # Check choices
        choices = Choice.objects.all()
        print(f"🔘 Choices: {choices.count()}")

        return True

    except Exception as e:
        print(f"❌ Database operations failed: {e}")
        return False


def main():
    """Main test function"""
    print("🔧 LMS Quiz System Test Suite")
    print("=" * 40)

    # Test AI generation
    quiz_data = test_quiz_generation()

    # Test database
    db_ok = test_database_operations()

    print("\n📊 Test Summary:")
    print(f"   AI Generation: {'✅ PASS' if quiz_data else '❌ FAIL'}")
    print(f"   Database Ops:  {'✅ PASS' if db_ok else '❌ FAIL'}")

    if quiz_data and db_ok:
        print("\n🎉 All tests passed! Your quiz system is ready to use.")
        print("\n📋 Next steps:")
        print("   1. Run the Django development server")
        print("   2. Log in as an instructor")
        print("   3. Generate a quiz using AI Tools")
        print("   4. Save it to a course")
        print("   5. Have students take the quiz")
    else:
        print("\n⚠️ Some tests failed. Please check the setup.")


if __name__ == "__main__":
    main()
