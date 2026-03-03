from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import (
    UserProfile, Course, Assessment,
    AssessmentResult, UserCourseInteraction,
    LearningPath, Progress
)


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

    # Calculate score
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


# ── RECOMMEND ─────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        user_skills    = user_profile.skills
        user_interests = user_profile.interests
        user_level     = user_profile.experience_level
    except UserProfile.DoesNotExist:
        # No profile yet — return all beginner courses
        courses = Course.objects.filter(difficulty='beginner')[:5]
        return Response([{
            'id': c.id, 'title': c.title,
            'topic': c.topic, 'difficulty': c.difficulty,
            'url': c.url, 'rating': c.rating
        } for c in courses])

    # Get courses matching interests and level
    matched = Course.objects.filter(
        difficulty=user_level
    )

    # Filter by interests if available
    if user_interests:
        from django.db.models import Q
        query = Q()
        for interest in user_interests:
            query |= Q(topic__icontains=interest)
        matched = matched.filter(query)

    # Exclude already completed courses
    completed_ids = UserCourseInteraction.objects.filter(
        user=request.user, completed=True
    ).values_list('course_id', flat=True)

    matched = matched.exclude(id__in=completed_ids).order_by('-rating')[:6]

    # Fallback if no matches
    if not matched:
        matched = Course.objects.exclude(
            id__in=completed_ids
        ).order_by('-rating')[:6]

    return Response([{
        'id':         c.id,
        'title':      c.title,
        'topic':      c.topic,
        'difficulty': c.difficulty,
        'url':        c.url,
        'rating':     c.rating,
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

    interaction, _ = UserCourseInteraction.objects.update_or_create(
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