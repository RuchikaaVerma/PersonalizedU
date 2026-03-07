from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────
    path('register/',                       views.register,             name='register'),

    # ── Profile ───────────────────────────────────────
    path('profile/',                        views.profile,              name='profile'),

    # ── Courses ───────────────────────────────────────
    path('courses/',                        views.courses,              name='courses'),
    path('courses/<int:pk>/explain/',       views.explain_course,       name='explain-course'),

    # ── Assessment ────────────────────────────────────
    path('assessment/<int:pk>/',            views.get_assessment,       name='assessment'),
    path('assessment/submit/',              views.submit_assessment,    name='submit-assessment'),
    path('generate-assessment/',            views.generate_assessment,  name='generate-assessment'),

    # ── Recommendations ───────────────────────────────
    path('recommend/',                      views.recommend,            name='recommend'),
    path('ai-recommend/',                   views.ai_recommend,         name='ai-recommend'),

    # ── Progress & Interaction ────────────────────────
    path('progress/',                       views.get_progress,         name='progress'),
    path('interaction/',                    views.log_interaction,      name='interaction'),

    # ── Ollama Chat ───────────────────────────────────
    path('chat/',                           views.ollama_chat,          name='ollama-chat'),
]