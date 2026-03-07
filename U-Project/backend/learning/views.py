import json
import re
import requests

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import (
    UserProfile, Course, Assessment,
    AssessmentResult, UserCourseInteraction,
    LearningPath, Progress
)


# ── OLLAMA CONFIG ─────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434/v1/chat/completions"
OLLAMA_MODEL = "tinyllama"


def call_ollama(messages, max_tokens=512, temperature=0.7):
    """
    Helper — calls local Ollama and returns the reply string.
    Raises requests.exceptions.ConnectionError if Ollama is not running.
    """
    resp = requests.post(
        OLLAMA_URL,
        json={
            "model":       OLLAMA_MODEL,
            "messages":    messages,
            "max_tokens":  max_tokens,
            "temperature": temperature,
            "stream":      False,
        },
        timeout=60,
    )
    print("Ollama status:", resp.status_code)       # visible in Django terminal
    print("Ollama response:", resp.text[:300])      # visible in Django terminal
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


# ── AUTH ──────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    email    = request.data.get('email')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Username and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    UserProfile.objects.create(user=user)

    return Response(
        {'message': f'User {username} created successfully'},
        status=status.HTTP_201_CREATED
    )


# ── PROFILE ───────────────────────────────────────────

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        return Response({
            'username':         request.user.username,
            'email':            request.user.email,
            'experience_level': user_profile.experience_level,
            'skills':           user_profile.skills,
            'interests':        user_profile.interests,
            'goals':            user_profile.goals,
        })

    if request.method == 'PUT':
        user_profile.experience_level = request.data.get(
            'experience_level', user_profile.experience_level
        )
        user_profile.skills    = request.data.get('skills',    user_profile.skills)
        user_profile.interests = request.data.get('interests', user_profile.interests)
        user_profile.goals     = request.data.get('goals',     user_profile.goals)
        user_profile.save()

        return Response({'message': 'Profile updated successfully'})


# ── COURSES ───────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def courses(request):
    topic      = request.query_params.get('topic', None)
    difficulty = request.query_params.get('difficulty', None)

    all_courses = Course.objects.all()

    if topic:
        all_courses = all_courses.filter(topic__icontains=topic)
    if difficulty:
        all_courses = all_courses.filter(difficulty=difficulty)

    data = [{
        'id':               c.id,
        'title':            c.title,
        'description':      c.description,
        'topic':            c.topic,
        'difficulty':       c.difficulty,
        'url':              c.url,
        'duration_minutes': c.duration_minutes,
        'rating':           c.rating,
    } for c in all_courses]

    return Response(data)


# ── ASSESSMENT ────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def get_assessment(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk)
    return Response({
        'id':        assessment.id,
        'title':     assessment.title,
        'topic':     assessment.topic,
        'questions': assessment.questions,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_assessment(request):
    assessment_id = request.data.get('assessment_id')
    user_answers  = request.data.get('answers', {})

    assessment = get_object_or_404(Assessment, pk=assessment_id)
    questions  = assessment.questions

    correct = 0
    for i, q in enumerate(questions):
        if user_answers.get(str(i)) == q.get('answer'):
            correct += 1

    score = int((correct / len(questions)) * 100) if questions else 0

    AssessmentResult.objects.create(
        user=request.user,
        assessment=assessment,
        score=score,
        answers=user_answers
    )

    return Response({
        'score':   score,
        'correct': correct,
        'total':   len(questions),
        'message': f'You scored {score}%'
    })


# ── RECOMMEND (rule-based) ────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend(request):
    try:
        user_profile   = UserProfile.objects.get(user=request.user)
        user_interests = user_profile.interests
        user_level     = user_profile.experience_level
    except UserProfile.DoesNotExist:
        fallback = Course.objects.filter(difficulty='beginner')[:5]
        return Response([{
            'id': c.id, 'title': c.title,
            'topic': c.topic, 'difficulty': c.difficulty,
            'url': c.url, 'rating': c.rating
        } for c in fallback])

    matched = Course.objects.filter(difficulty=user_level)

    if user_interests:
        query = Q()
        for interest in user_interests:
            query |= Q(topic__icontains=interest)
        matched = matched.filter(query)

    completed_ids = UserCourseInteraction.objects.filter(
        user=request.user, completed=True
    ).values_list('course_id', flat=True)

    matched = matched.exclude(id__in=completed_ids).order_by('-rating')[:6]

    if not matched:
        matched = Course.objects.exclude(
            id__in=completed_ids
        ).order_by('-rating')[:6]

    return Response([{
        'id':               c.id,
        'title':            c.title,
        'topic':            c.topic,
        'difficulty':       c.difficulty,
        'url':              c.url,
        'rating':           c.rating,
        'duration_minutes': c.duration_minutes,
    } for c in matched])


# ── PROGRESS ──────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_progress(request):
    progress_items = Progress.objects.filter(user=request.user)

    data = [{
        'course_id':        p.course.id,
        'course_title':     p.course.title,
        'topic':            p.course.topic,
        'percent_complete': p.percent_complete,
        'last_accessed':    p.last_accessed,
    } for p in progress_items]

    return Response(data)


# ── INTERACTION ───────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_interaction(request):
    course_id       = request.data.get('course_id')
    completed       = request.data.get('completed', False)
    rating          = request.data.get('rating', None)
    time_spent_mins = request.data.get('time_spent_mins', 0)
    percent         = request.data.get('percent_complete', 0)

    course = get_object_or_404(Course, pk=course_id)

    UserCourseInteraction.objects.update_or_create(
        user=request.user,
        course=course,
        defaults={
            'completed':       completed,
            'rating':          rating,
            'time_spent_mins': time_spent_mins,
        }
    )

    Progress.objects.update_or_create(
        user=request.user,
        course=course,
        defaults={'percent_complete': percent}
    )

    return Response({'message': 'Interaction logged successfully'})


# ══════════════════════════════════════════════════════
#   OLLAMA-POWERED ENDPOINTS
# ══════════════════════════════════════════════════════

# ── CHAT (proxy for frontend) ─────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def ollama_chat(request):
    messages    = request.data.get('messages', [])
    max_tokens  = request.data.get('max_tokens', 512)
    temperature = request.data.get('temperature', 0.7)

    if not messages:
        return Response(
            {'error': 'messages field is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ── Fix: TinyLlama doesn't support 'system' role ──
    # Convert system messages to user messages so TinyLlama doesn't crash
    cleaned = []
    for m in messages:
        if m.get('role') == 'system':
            cleaned.append({
                'role':    'user',
                'content': f"[System instructions]: {m['content']}"
            })
        elif m.get('role') == 'assistant':
            # TinyLlama uses 'assistant' correctly — keep as-is
            cleaned.append(m)
        else:
            cleaned.append(m)

    try:
        reply = call_ollama(cleaned, max_tokens=max_tokens, temperature=temperature)
        return Response({
            "choices": [{
                "message": {
                    "role":    "assistant",
                    "content": reply
                }
            }]
        })

    except requests.exceptions.ConnectionError:
        return Response(
            {'error': 'Ollama is not running. Start it with: ollama serve'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ── AI RECOMMEND (Ollama explains WHY) ───────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_recommend(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'Please complete your profile first.'},
            status=status.HTTP_404_NOT_FOUND
        )

    prompt = f"""
A learner has the following profile:
- Experience level : {user_profile.experience_level}
- Current skills   : {', '.join(user_profile.skills)   or 'none listed'}
- Interests        : {', '.join(user_profile.interests) or 'none listed'}
- Goals            : {', '.join(user_profile.goals)     or 'none listed'}

Suggest exactly 3 specific learning topics they should focus on next.
For each topic give a one-sentence reason tailored to their profile.

Respond ONLY with a valid JSON array — no markdown, no explanation:
[{{"topic": "...", "reason": "..."}}, ...]
""".strip()

    try:
        raw = call_ollama(
            [{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.5,
        )
        clean = re.sub(r'```(?:json)?|```', '', raw).strip()
        match = re.search(r'\[.*\]', clean, re.DOTALL)
        suggestions = json.loads(match.group()) if match else []
        return Response({'ai_suggestions': suggestions})

    except requests.exceptions.ConnectionError:
        return Response(
            {'error': 'Ollama is not running. Start it with: ollama serve'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except (json.JSONDecodeError, AttributeError):
        return Response({'ai_suggestions': [], 'raw': raw})
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ── AI ASSESSMENT GENERATOR ───────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_assessment(request):
    topic         = request.data.get('topic', 'General Programming')
    num_questions = min(int(request.data.get('num_questions', 5)), 10)

    prompt = f"""
Create a multiple-choice quiz about "{topic}" with exactly {num_questions} questions.

Rules:
- Each question has exactly 4 options labelled A, B, C, D.
- The answer field must be the full text of the correct option (not just A/B/C/D).
- Questions should be appropriate for a learner.

Respond ONLY with a valid JSON array — no markdown, no explanation:
[
  {{
    "question": "...",
    "options":  ["...", "...", "...", "..."],
    "answer":   "..."
  }}
]
""".strip()

    try:
        raw   = call_ollama(
            [{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.6,
        )
        clean = re.sub(r'```(?:json)?|```', '', raw).strip()
        match = re.search(r'\[.*\]', clean, re.DOTALL)
        questions = json.loads(match.group()) if match else []

        return Response({
            'topic':     topic,
            'questions': questions,
        })

    except requests.exceptions.ConnectionError:
        return Response(
            {'error': 'Ollama is not running. Start it with: ollama serve'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except (json.JSONDecodeError, AttributeError):
        return Response({'questions': [], 'raw': raw})
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ── AI COURSE EXPLAINER ───────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def explain_course(request, pk):
    course = get_object_or_404(Course, pk=pk)

    prompt = f"""
Explain the following course to a {course.difficulty}-level learner in 2-3 short paragraphs:

Course title : {course.title}
Topic        : {course.topic}
Description  : {course.description}

Focus on: what they will learn, why it matters, and what they can build after completing it.
Keep the tone friendly and encouraging.
""".strip()

    try:
        explanation = call_ollama(
            [{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.6,
        )
        return Response({
            'course_id':    course.id,
            'course_title': course.title,
            'explanation':  explanation,
        })

    except requests.exceptions.ConnectionError:
        return Response(
            {'error': 'Ollama is not running. Start it with: ollama serve'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )