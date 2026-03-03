from django.contrib import admin
from .models import (
    UserProfile, Course, Assessment,
    AssessmentResult, UserCourseInteraction,
    LearningPath, Progress
)

admin.site.register(UserProfile)
admin.site.register(Course)
admin.site.register(Assessment)
admin.site.register(AssessmentResult)
admin.site.register(UserCourseInteraction)
admin.site.register(LearningPath)
admin.site.register(Progress)