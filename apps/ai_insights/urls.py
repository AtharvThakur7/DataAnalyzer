from django.urls import path
from . import views

urlpatterns = [
    path('ask/', views.ask_question, name='ai_ask'),
    path('insights/', views.generate_insights, name='ai_insights'),
    path('suggest-charts/', views.suggest_charts, name='ai_suggest_charts'),
    path('report/', views.generate_report, name='ai_report'),
]
