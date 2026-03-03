from django.urls import path
from . import views

urlpatterns = [
    path('register/',               views.register,          name='register'),
    path('profile/',                views.profile,           name='profile'),
    path('courses/',                views.courses,           name='courses'),
    path('assessment/<int:pk>/',    views.get_assessment,    name='assessment'),
    path('assessment/submit/',      views.submit_assessment, name='submit-assessment'),
    path('recommend/',              views.recommend,         name='recommend'),
    path('progress/',               views.get_progress,      name='progress'),
    path('interaction/',            views.log_interaction,   name='interaction'),
]