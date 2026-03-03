from django.db import models
from django.contrib.auth.models import User


# ── User Profile ──────────────────────────────────────
class UserProfile(models.Model):
    EXPERIENCE_CHOICES = [
        ('beginner',     'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced',     'Advanced'),
    ]

    user             = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='beginner')
    skills           = models.JSONField(default=list)   # e.g. ["Python", "HTML"]
    interests        = models.JSONField(default=list)   # e.g. ["AI", "Web Dev"]
    goals            = models.JSONField(default=list)   # e.g. ["Get a job in data science"]
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Profile"


# ── Course ────────────────────────────────────────────
class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner',     'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced',     'Advanced'),
    ]

    title            = models.CharField(max_length=255)
    description      = models.TextField()
    topic            = models.CharField(max_length=100)   # e.g. "Python", "Data Science"
    difficulty       = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    url              = models.URLField(blank=True)
    duration_minutes = models.IntegerField(default=0)
    rating           = models.FloatField(default=0.0)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.topic})"


# ── Assessment ────────────────────────────────────────
class Assessment(models.Model):
    title       = models.CharField(max_length=255)
    topic       = models.CharField(max_length=100)
    questions   = models.JSONField(default=list)
    # questions format:
    # [
    #   {
    #     "question": "What is a list in Python?",
    #     "options":  ["A loop", "A data type", "A function", "A class"],
    #     "answer":   "A data type"
    #   }
    # ]
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.topic}"


# ── Assessment Result ─────────────────────────────────
class AssessmentResult(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_results')
    assessment   = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    score        = models.IntegerField(default=0)        # percentage 0-100
    answers      = models.JSONField(default=dict)        # user's submitted answers
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.assessment.title} - {self.score}%"


# ── User Course Interaction ───────────────────────────
class UserCourseInteraction(models.Model):
    user             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    course           = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed        = models.BooleanField(default=False)
    rating           = models.IntegerField(null=True, blank=True)  # 1-5 stars
    time_spent_mins  = models.IntegerField(default=0)
    interacted_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} → {self.course.title}"


# ── Learning Path ─────────────────────────────────────
class LearningPath(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_paths')
    title      = models.CharField(max_length=255)
    courses    = models.ManyToManyField(Course, blank=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"


# ── Progress ──────────────────────────────────────────
class Progress(models.Model):
    user             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    course           = models.ForeignKey(Course, on_delete=models.CASCADE)
    percent_complete = models.IntegerField(default=0)    # 0-100
    last_accessed    = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.percent_complete}%"