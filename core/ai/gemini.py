import json
import logging
import re
import time
from datetime import datetime, timedelta
from functools import wraps

from django.conf import settings
from django.core.cache import cache

import google.generativeai as genai

# Set up logging
logger = logging.getLogger(__name__)

# Mock data for fallback when API is unavailable
MOCK_QUIZ_DATA = {
    "multiple_choice": {
        "history": [
            {
                "order": 1,
                "type": "multiple_choice",
                "text": "Which event marked the beginning of World War II?",
                "choices": [
                    {"letter": "A", "text": "Pearl Harbor attack"},
                    {"letter": "B", "text": "German invasion of Poland"},
                    {"letter": "C", "text": "Battle of Britain"},
                    {"letter": "D", "text": "D-Day landings"},
                ],
                "correct_answer": "B",
                "explanation": "Germany invaded Poland on September 1, 1939, which prompted Britain and France to declare war on Germany.",
            },
            {
                "order": 2,
                "type": "multiple_choice",
                "text": "Who was the first President of the United States?",
                "choices": [
                    {"letter": "A", "text": "Thomas Jefferson"},
                    {"letter": "B", "text": "George Washington"},
                    {"letter": "C", "text": "John Adams"},
                    {"letter": "D", "text": "Benjamin Franklin"},
                ],
                "correct_answer": "B",
                "explanation": "George Washington served as the first President from 1789 to 1797.",
            },
        ],
        "science": [
            {
                "order": 1,
                "type": "multiple_choice",
                "text": "What is the chemical symbol for water?",
                "choices": [
                    {"letter": "A", "text": "H2O"},
                    {"letter": "B", "text": "CO2"},
                    {"letter": "C", "text": "O2"},
                    {"letter": "D", "text": "N2"},
                ],
                "correct_answer": "A",
                "explanation": "Water consists of two hydrogen atoms and one oxygen atom, hence H2O.",
            },
            {
                "order": 2,
                "type": "multiple_choice",
                "text": "Which planet is closest to the Sun?",
                "choices": [
                    {"letter": "A", "text": "Venus"},
                    {"letter": "B", "text": "Earth"},
                    {"letter": "C", "text": "Mercury"},
                    {"letter": "D", "text": "Mars"},
                ],
                "correct_answer": "C",
                "explanation": "Mercury is the innermost planet in our solar system.",
            },
        ],
    },
    "true_false": [
        {
            "order": 1,
            "type": "true_false",
            "text": "The Earth revolves around the Sun.",
            "correct_answer": True,
            "explanation": "The Earth orbits the Sun in an elliptical path, completing one revolution in about 365.25 days.",
        },
        {
            "order": 2,
            "type": "true_false",
            "text": "Photosynthesis occurs only in the dark.",
            "correct_answer": False,
            "explanation": "Photosynthesis requires light energy and primarily occurs during daylight hours.",
        },
    ],
    "short_answer": [
        {
            "order": 1,
            "type": "short_answer",
            "text": "Explain the process of photosynthesis.",
            "sample_answer": "Photosynthesis is the process by which plants convert light energy into chemical energy. It involves the absorption of carbon dioxide and water to produce glucose and oxygen using chlorophyll.",
        },
        {
            "order": 2,
            "type": "short_answer",
            "text": "What are the main causes of climate change?",
            "sample_answer": "The main causes include greenhouse gas emissions from burning fossil fuels, deforestation, industrial processes, and agricultural practices that increase atmospheric CO2 levels.",
        },
    ],
}


def get_fallback_quiz_data(topic, num_questions, question_type):
    """Generate fallback quiz data when API is unavailable."""

    # Determine category based on topic keywords
    topic_lower = topic.lower()
    if any(
        word in topic_lower
        for word in ["history", "war", "president", "ancient", "medieval"]
    ):
        category = "history"
    elif any(
        word in topic_lower
        for word in ["science", "biology", "chemistry", "physics", "planet"]
    ):
        category = "science"
    else:
        category = "science"  # default

    if question_type == "multiple_choice":
        questions = MOCK_QUIZ_DATA["multiple_choice"].get(
            category, MOCK_QUIZ_DATA["multiple_choice"]["science"]
        )
    else:
        questions = MOCK_QUIZ_DATA[question_type]

    # Select requested number of questions
    selected_questions = questions[: min(num_questions, len(questions))]

    # Generate mock raw text
    raw_text = "\n---\n".join(
        [
            f"QUESTION: {q['text']}\n"
            + (
                "\n".join(
                    [
                        f"{choice['letter']}) {choice['text']}"
                        for choice in q.get("choices", [])
                    ]
                )
                + f"\nCORRECT: {q.get('correct_answer', '')}\nEXPLANATION: {q.get('explanation', '')}"
                if question_type == "multiple_choice"
                else (
                    f"CORRECT: {q.get('correct_answer', '')}\nEXPLANATION: {q.get('explanation', '')}"
                    if question_type == "true_false"
                    else f"SAMPLE_ANSWER: {q.get('sample_answer', '')}"
                )
            )
            for q in selected_questions
        ]
    )

    return {
        "topic": topic,
        "question_type": question_type,
        "num_questions": len(selected_questions),
        "questions": raw_text,
        "parsed_questions": selected_questions,
        "is_demo": True,
        "demo_message": "This is demo content. Gemini API quota exceeded - upgrade your plan for AI-generated content.",
    }


def get_fallback_lesson_plan(topic, duration, difficulty_level):
    """Generate fallback lesson plan when API is unavailable."""

    content = f"""# Lesson Plan: {topic}

**Duration:** {duration}
**Difficulty Level:** {difficulty_level}

## Learning Objectives
By the end of this lesson, students will be able to:
1. Understand the fundamental concepts of {topic}
2. Apply basic principles in practical scenarios
3. Demonstrate knowledge through guided activities

## Materials Needed
- Whiteboard/markers
- Handouts and worksheets
- Computer/projector for presentations
- Reference materials

## Lesson Structure

### Introduction (10 minutes)
- Welcome and attendance
- Review previous lesson connections
- Introduce today's topic: {topic}
- Preview learning objectives

### Main Content (35 minutes)

#### Part 1: Core Concepts
- Define key terms related to {topic}
- Explain fundamental principles
- Provide examples and non-examples

#### Part 2: Practical Application
- Demonstrate real-world applications
- Interactive discussion with students
- Address common questions and misconceptions

### Activities (10 minutes)
- Small group discussion
- Quick practice exercises
- Peer teaching opportunities

### Assessment (5 minutes)
- Quick formative assessment
- Exit ticket with 2-3 questions
- Student self-reflection

## Conclusion
- Summarize key points
- Preview next lesson
- Assign homework/follow-up reading

## Homework/Follow-up
- Read pages XX-XX in textbook
- Complete practice worksheet
- Prepare questions for next class

Note: This is a template lesson plan. Adapt content and timing based on your specific curriculum and student needs."""

    return {
        "topic": topic,
        "duration": duration,
        "difficulty": difficulty_level,
        "content": content,
        "is_demo": True,
        "demo_message": "This is demo content. Gemini API quota exceeded - upgrade your plan for AI-generated content.",
    }


def get_fallback_rubric(assignment_description, grading_criteria):
    """Generate fallback rubric when API is unavailable."""

    content = f"""# Grading Rubric

**Assignment:** {assignment_description}
**Key Criteria:** {grading_criteria}

| Criteria | Excellent (4) | Good (3) | Satisfactory (2) | Needs Improvement (1) |
|----------|---------------|----------|------------------|----------------------|
| Content Knowledge | Demonstrates comprehensive understanding with detailed explanations and examples | Shows good understanding with adequate explanations | Basic understanding with minimal explanations | Limited understanding with unclear explanations |
| Organization | Clear, logical structure with smooth transitions | Well-organized with some transitions | Adequate organization with few transitions | Poor organization, difficult to follow |
| Quality of Work | Exceptional quality, exceeds expectations | High quality, meets all expectations | Acceptable quality, meets most expectations | Below average quality, meets few expectations |
| Creativity/Innovation | Highly creative with original ideas | Creative with some original elements | Some creativity evident | Little to no creativity |
| Technical Skills | Advanced technical proficiency | Good technical skills | Basic technical competency | Limited technical skills |

## Point Distribution
- Excellent (4): 90-100 points
- Good (3): 80-89 points  
- Satisfactory (2): 70-79 points
- Needs Improvement (1): Below 70 points

## Total Points: ___/100

## Additional Comments:
_Space for instructor feedback and suggestions for improvement_

Note: This is a template rubric. Customize criteria and point values based on your specific assignment requirements."""

    return content


def get_fallback_explanation(concept, grade_level):
    """Generate fallback concept explanation when API is unavailable."""

    content = f"""# Understanding {concept}

## What is {concept}?
{concept} is a fundamental concept that plays an important role in this subject area. Understanding this concept is essential for building a strong foundation in the field.

## Key Characteristics
- **Definition**: {concept} can be defined as [core definition appropriate for {grade_level} level]
- **Properties**: Key properties and characteristics that define this concept
- **Components**: Main elements or parts that make up {concept}

## Real-World Examples

### Example 1: Daily Life Application
You encounter {concept} in everyday situations. For instance, when you [specific example relevant to the concept].

### Example 2: Professional Context
In professional settings, {concept} is used to [professional application example].

## Why is {concept} Important?

1. **Foundational Knowledge**: Understanding {concept} helps build knowledge in related areas
2. **Practical Applications**: This concept has many real-world applications
3. **Problem Solving**: Knowing {concept} helps solve complex problems in the field
4. **Critical Thinking**: Develops analytical and reasoning skills

## Common Misconceptions

❌ **Misconception**: Students often think [common misconception]
✅ **Reality**: Actually, [correct understanding]

❌ **Misconception**: Another common error is believing [another misconception]
✅ **Reality**: The truth is [correct explanation]

## Practice Questions

1. How would you explain {concept} to someone unfamiliar with the topic?
2. Can you think of three examples of {concept} in your daily life?
3. What are the most important aspects to remember about {concept}?

## Further Learning
- Explore related concepts and how they connect to {concept}
- Practice applying this knowledge in different contexts
- Discuss with peers to deepen understanding

Note: This is a template explanation. For detailed, subject-specific content, consult your textbooks and additional resources."""

    return content


def get_fallback_syllabus(course_title, duration, topics_list):
    """Generate fallback syllabus when API is unavailable."""

    topics = [topic.strip() for topic in topics_list.split(",")]

    content = f"""# Course Syllabus: {course_title}

## Course Information
- **Course Title**: {course_title}
- **Duration**: {duration}
- **Instructor**: [Instructor Name]
- **Contact**: [Email] | [Phone] | [Office Hours]

## Course Description
This course provides a comprehensive introduction to {course_title}. Students will explore key concepts, develop practical skills, and gain hands-on experience in the field. The course combines theoretical knowledge with practical applications to prepare students for real-world challenges.

## Learning Objectives
Upon successful completion of this course, students will be able to:
1. Demonstrate understanding of fundamental concepts in {course_title}
2. Apply theoretical knowledge to practical situations
3. Analyze complex problems and develop effective solutions
4. Communicate ideas clearly and professionally
5. Work effectively both independently and in teams

## Course Outline

### Week 1-2: Introduction and Foundations
- Course overview and expectations
- {topics[0] if topics else "Fundamental concepts"}
- Historical background and context

### Week 3-4: Core Concepts
- {topics[1] if len(topics) > 1 else "Key theories and principles"}
- Practical applications and examples
- Case studies and analysis

### Week 5-6: Advanced Topics
- {topics[2] if len(topics) > 2 else "Advanced concepts and techniques"}
- Research methods and best practices
- Industry standards and regulations

### Week 7-8: Practical Applications
- {topics[3] if len(topics) > 3 else "Hands-on projects and activities"}
- Group work and collaboration
- Problem-solving exercises

### Week 9-10: Integration and Assessment
- Synthesis of course materials
- Final project presentations
- Course review and evaluation

## Assessment Methods

| Assessment Type | Weight | Description |
|----------------|--------|-------------|
| Participation | 10% | Class attendance and engagement |
| Assignments | 30% | Regular homework and exercises |
| Midterm Exam | 25% | Comprehensive mid-course assessment |
| Final Project | 25% | Capstone project demonstrating learning |
| Final Exam | 10% | Cumulative final assessment |

## Grading Scale
- A: 90-100%
- B: 80-89%
- C: 70-79% 
- D: 60-69%
- F: Below 60%

## Required Materials
- Textbook: [Title, Author, Edition]
- Course packet (available at bookstore)
- Access to computer and internet
- Notebook and writing materials

## Course Policies

### Attendance
- Regular attendance is expected and required
- More than 3 unexcused absences may result in course failure
- Notify instructor in advance for planned absences

### Late Work
- Late assignments will be penalized 10% per day
- Extensions may be granted for documented emergencies
- Final project cannot be submitted late

### Academic Integrity
- All work must be original and properly cited
- Plagiarism will result in course failure
- Collaboration is encouraged but must be acknowledged

## Schedule Overview

**Important Dates:**
- Midterm Exam: [Date]
- Final Project Due: [Date]
- Final Exam: [Date]
- No classes: [Holiday dates]

## Student Support
- Office hours: [Days and times]
- Tutoring services available through [Resource]
- Accommodation services: Contact [Office]

Note: This syllabus is subject to change. Students will be notified of any modifications in advance.

*This is a template syllabus. Customize dates, requirements, and policies according to your institution's guidelines.*"""

    return content


# Rate limiting decorator
def rate_limit_gemini(max_requests_per_minute=10):
    """
    Decorator to implement rate limiting for Gemini API calls.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"gemini_rate_limit_{func.__name__}"
            current_requests = cache.get(cache_key, 0)

            if current_requests >= max_requests_per_minute:
                logger.warning(f"Rate limit exceeded for {func.__name__}. Waiting...")
                return {
                    "error": "Rate limit exceeded. Please wait a moment before trying again.",
                    "rate_limited": True,
                }

            # Increment counter
            cache.set(cache_key, current_requests + 1, 60)  # Reset every minute

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    logger.error(f"Quota exceeded in {func.__name__}: {error_str}")
                    # Extract retry delay if available
                    retry_delay = extract_retry_delay(error_str)
                    return {
                        "error": "API quota exceeded. Please try again later.",
                        "quota_exceeded": True,
                        "retry_after": retry_delay,
                        "details": "You have exceeded the Gemini API quota limits. Consider upgrading your plan or waiting for the quota to reset.",
                    }
                raise e

        return wrapper

    return decorator


def extract_retry_delay(error_message):
    """
    Extract retry delay from error message if available.
    """
    try:
        if "seconds:" in error_message:
            import re

            match = re.search(r"seconds: (\d+)", error_message)
            if match:
                return int(match.group(1))
        return 60  # Default to 1 minute
    except:
        return 60


# Configure Gemini AI API
def configure_gemini():
    """
    Configures the Gemini API with the key from Django settings.
    """
    api_key = getattr(settings, "GEMINI_API_KEY", None)
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found in settings.py or environment variables."
        )
    genai.configure(api_key=api_key)


# Generate exam content using Gemini AI
@rate_limit_gemini(max_requests_per_minute=8)
def generate_exam_content(prompt_text):
    """
    Generates exam questions using Gemini AI from a given prompt.

    Args:
        prompt_text (str): The prompt to send to Gemini.

    Returns:
        list: A list of dictionaries with 'question_text' and 'answer'.
    """
    configure_gemini()

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt_text)
        text = response.text if hasattr(response, "text") else str(response)

        # For now, we just return mock content. Replace this with a real parser.
        return [
            {"question_text": q.strip(), "answer": "Sample answer"}
            for q in text.split("\n")
            if q.strip()
        ]

    except Exception as e:
        return [{"question_text": f"Error: {str(e)}", "answer": ""}]


@rate_limit_gemini(max_requests_per_minute=8)
def generate_lesson_plan(topic, duration, difficulty_level):
    """
    Generate a structured lesson plan using Gemini AI.

    Args:
        topic (str): The lesson topic
        duration (str): Duration of the lesson (e.g., "60 minutes")
        difficulty_level (str): Beginner, Intermediate, or Advanced

    Returns:
        dict: Structured lesson plan
    """
    configure_gemini()

    prompt = f"""
    Create a detailed lesson plan for the topic: {topic}
    Duration: {duration}
    Difficulty Level: {difficulty_level}
    
    Please structure the lesson plan with the following sections:
    1. Learning Objectives
    2. Materials Needed
    3. Introduction (5-10 minutes)
    4. Main Content (split into logical sections)
    5. Activities/Exercises
    6. Assessment Methods
    7. Conclusion/Summary
    8. Homework/Follow-up
    
    Make it practical and engaging for students.
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return {
            "topic": topic,
            "duration": duration,
            "difficulty": difficulty_level,
            "content": response.text,
        }
    except Exception as e:
        return {"error": str(e)}


@rate_limit_gemini(max_requests_per_minute=8)
def generate_quiz_questions(topic, num_questions=5, question_type="multiple_choice"):
    """
    Generate quiz questions on a specific topic.

    Args:
        topic (str): The topic for questions
        num_questions (int): Number of questions to generate
        question_type (str): Type of questions (multiple_choice, true_false, short_answer)

    Returns:
        dict: Structured quiz data with parsed questions
    """
    configure_gemini()

    if question_type == "multiple_choice":
        prompt = f"""
        Create {num_questions} multiple choice questions about {topic}.
        Format each question EXACTLY as follows (no extra formatting):
        
        QUESTION: [Question text]
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        CORRECT: [A/B/C/D]
        EXPLANATION: [Brief explanation]
        ---
        
        Please ensure each question follows this exact format.
        """
    elif question_type == "true_false":
        prompt = f"""
        Create {num_questions} true/false questions about {topic}.
        Format each question EXACTLY as follows:
        
        QUESTION: [Statement]
        CORRECT: [True/False]
        EXPLANATION: [Brief explanation]
        ---
        
        Please ensure each question follows this exact format.
        """
    else:  # short_answer
        prompt = f"""
        Create {num_questions} short answer questions about {topic}.
        Format each question EXACTLY as follows:
        
        QUESTION: [Question text]
        SAMPLE_ANSWER: [Sample answer in 2-3 sentences]
        ---
        
        Please ensure each question follows this exact format.
        """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        # Parse the response into structured data
        parsed_questions = parse_quiz_response(response.text, question_type)

        return {
            "topic": topic,
            "question_type": question_type,
            "num_questions": num_questions,
            "questions": response.text,
            "parsed_questions": parsed_questions,
        }
    except Exception as e:
        error_str = str(e)

        # Check if it's a quota or rate limit error
        if (
            "429" in error_str
            or "quota" in error_str.lower()
            or "exceeded" in error_str.lower()
        ):
            logger.warning(
                f"Quota/rate limit exceeded, using fallback data: {error_str}"
            )

            # Return fallback quiz data instead of error
            fallback_data = get_fallback_quiz_data(topic, num_questions, question_type)

            # Add quota exceeded info
            fallback_data.update(
                {
                    "quota_exceeded": True,
                    "error_details": "Gemini API quota exceeded. Showing demo content. Upgrade your API plan for unlimited AI generation.",
                    "retry_after": extract_retry_delay(error_str),
                }
            )

            return fallback_data

        # For other errors, return error dict
        return {"error": error_str}


def parse_quiz_response(response_text, question_type):
    """
    Parse AI response into structured question data.

    Args:
        response_text (str): Raw AI response
        question_type (str): Type of questions

    Returns:
        list: List of structured question dictionaries
    """
    questions = []

    try:
        # Split by separator
        question_blocks = response_text.split("---")

        for i, block in enumerate(question_blocks):
            block = block.strip()
            if not block:
                continue

            question_data = {"order": i + 1, "type": question_type}

            if question_type == "multiple_choice":
                question_data = parse_multiple_choice(block, i + 1)
            elif question_type == "true_false":
                question_data = parse_true_false(block, i + 1)
            else:  # short_answer
                question_data = parse_short_answer(block, i + 1)

            if question_data:
                questions.append(question_data)

    except Exception as e:
        print(f"Error parsing quiz response: {e}")

    return questions


def parse_multiple_choice(block, order):
    """Parse multiple choice question block."""
    lines = [line.strip() for line in block.split("\n") if line.strip()]

    question_text = ""
    choices = []
    correct_answer = ""
    explanation = ""

    for line in lines:
        if line.startswith("QUESTION:"):
            question_text = line.replace("QUESTION:", "").strip()
        elif line.startswith(("A)", "B)", "C)", "D)")):
            choice_letter = line[0]
            choice_text = line[3:].strip()
            choices.append({"letter": choice_letter, "text": choice_text})
        elif line.startswith("CORRECT:"):
            correct_answer = line.replace("CORRECT:", "").strip()
        elif line.startswith("EXPLANATION:"):
            explanation = line.replace("EXPLANATION:", "").strip()

    if question_text and choices:
        return {
            "order": order,
            "type": "multiple_choice",
            "text": question_text,
            "choices": choices,
            "correct_answer": correct_answer,
            "explanation": explanation,
        }
    return None


def parse_true_false(block, order):
    """Parse true/false question block."""
    lines = [line.strip() for line in block.split("\n") if line.strip()]

    question_text = ""
    correct_answer = ""
    explanation = ""

    for line in lines:
        if line.startswith("QUESTION:"):
            question_text = line.replace("QUESTION:", "").strip()
        elif line.startswith("CORRECT:"):
            correct_answer = line.replace("CORRECT:", "").strip()
        elif line.startswith("EXPLANATION:"):
            explanation = line.replace("EXPLANATION:", "").strip()

    if question_text:
        return {
            "order": order,
            "type": "true_false",
            "text": question_text,
            "correct_answer": correct_answer.lower() == "true",
            "explanation": explanation,
        }
    return None


def parse_short_answer(block, order):
    """Parse short answer question block."""
    lines = [line.strip() for line in block.split("\n") if line.strip()]

    question_text = ""
    sample_answer = ""

    for line in lines:
        if line.startswith("QUESTION:"):
            question_text = line.replace("QUESTION:", "").strip()
        elif line.startswith("SAMPLE_ANSWER:"):
            sample_answer = line.replace("SAMPLE_ANSWER:", "").strip()

    if question_text:
        return {
            "order": order,
            "type": "short_answer",
            "text": question_text,
            "sample_answer": sample_answer,
        }
    return None


@rate_limit_gemini(max_requests_per_minute=8)
def generate_assignment_rubric(assignment_description, grading_criteria):
    """
    Generate a grading rubric for an assignment.

    Args:
        assignment_description (str): Description of the assignment
        grading_criteria (str): Key criteria to evaluate

    Returns:
        str: Generated rubric
    """
    configure_gemini()

    prompt = f"""
    Create a detailed grading rubric for the following assignment:
    
    Assignment: {assignment_description}
    
    Key Grading Criteria: {grading_criteria}
    
    Please create a rubric with:
    - 4 performance levels (Excellent, Good, Satisfactory, Needs Improvement)
    - Point values for each criterion
    - Clear descriptions of what constitutes each performance level
    - Total points possible
    
    Format it as a table or structured format that's easy to use for grading.
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating rubric: {str(e)}"


@rate_limit_gemini(max_requests_per_minute=8)
def explain_concept(concept, grade_level="college"):
    """
    Generate an explanation of a concept tailored to a specific grade level.

    Args:
        concept (str): The concept to explain
        grade_level (str): Target grade level

    Returns:
        str: Explanation of the concept
    """
    configure_gemini()

    prompt = f"""
    Explain the concept of "{concept}" in a way that's appropriate for {grade_level} level students.
    
    Please include:
    - A clear, simple definition
    - Key characteristics or components
    - Real-world examples or analogies
    - Why this concept is important
    - Common misconceptions (if any)
    
    Make the explanation engaging and easy to understand.
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error explaining concept: {str(e)}"


@rate_limit_gemini(max_requests_per_minute=8)
def generate_course_syllabus(course_title, duration, topics_list):
    """
    Generate a comprehensive course syllabus.

    Args:
        course_title (str): Title of the course
        duration (str): Course duration (e.g., "16 weeks")
        topics_list (str): Comma-separated list of topics to cover

    Returns:
        str: Generated syllabus
    """
    configure_gemini()

    prompt = f"""
    Create a comprehensive course syllabus for:
    
    Course Title: {course_title}
    Duration: {duration}
    Topics to Cover: {topics_list}
    
    Please include:
    1. Course Description
    2. Learning Objectives
    3. Course Outline (weekly breakdown)
    4. Assessment Methods
    5. Grading Scale
    6. Required Materials/Textbooks
    7. Course Policies (attendance, late work, etc.)
    8. Schedule of assignments and exams
    
    Make it professional and comprehensive.
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating syllabus: {str(e)}"
