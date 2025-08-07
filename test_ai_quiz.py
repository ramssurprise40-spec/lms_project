#!/usr/bin/env python
"""
Test script to verify AI quiz generation functionality
"""
import os
import sys

import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms_backend.settings")
django.setup()

from core.ai.gemini import generate_quiz_questions


def test_ai_quiz_generation():
    """Test the AI quiz generation with fallback"""
    print("Testing AI Quiz Generation...")
    print("=" * 50)

    # Test parameters
    topic = "Python Programming"
    difficulty = "beginner"
    num_questions = 3

    print(f"Topic: {topic}")
    print(f"Difficulty: {difficulty}")
    print(f"Number of questions: {num_questions}")
    print("-" * 30)

    try:
        # Call the AI quiz generation function
        result = generate_quiz_questions(topic, num_questions, "multiple_choice")

        print("✅ Quiz generation successful!")
        print(f"Generated {len(result)} questions")
        print()

        # Display the generated questions
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False

        questions = result.get("parsed_questions", [])
        print(f"Generated {len(questions)} questions")
        print()

        for i, question in enumerate(questions, 1):
            print(f"Question {i}:")
            print(f"  Text: {question['text']}")
            print(f"  Type: {question['type']}")
            if question["type"] == "multiple_choice":
                print("  Choices:")
                for choice in question["choices"]:
                    correct_marker = (
                        " ✓" if choice["letter"] == question["correct_answer"] else ""
                    )
                    print(f"    {choice['letter']}) {choice['text']}{correct_marker}")
                print(f"  Explanation: {question.get('explanation', 'N/A')}")
            print()

        return True

    except Exception as e:
        print(f"❌ Quiz generation failed: {str(e)}")
        return False


def test_different_scenarios():
    """Test different scenarios"""
    scenarios = [
        ("Machine Learning", "intermediate", 2),
        ("Web Development", "advanced", 2),
        ("Database Design", "beginner", 2),
    ]

    print("\nTesting Multiple Scenarios:")
    print("=" * 50)

    for topic, difficulty, num_questions in scenarios:
        print(f"\nTesting: {topic} ({difficulty})")
        try:
            result = generate_quiz_questions(topic, 2, "multiple_choice")
            if "error" not in result:
                questions = result.get("parsed_questions", [])
                print(f"✅ Success: Generated {len(questions)} questions")
            else:
                print(f"❌ Error: {result['error']}")
        except Exception as e:
            print(f"❌ Failed: {str(e)}")


if __name__ == "__main__":
    print("AI Quiz Generation Test")
    print("=" * 50)

    # Test basic functionality
    success = test_ai_quiz_generation()

    if success:
        # Test multiple scenarios
        test_different_scenarios()

        print("\n" + "=" * 50)
        print("🎉 All tests completed!")
        print("You can now:")
        print("1. Visit http://127.0.0.1:8000/ai/quiz-generator/ to test in browser")
        print("2. Login as an instructor and generate quizzes")
        print("3. Save generated quizzes to courses")
        print("4. Let students take the quizzes")
    else:
        print("\n❌ Basic test failed. Please check the AI configuration.")
