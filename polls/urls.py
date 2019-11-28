from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sub', views.sub, name='sub'),
    path('line_chart', views.line_chart, name='line_chart'),
    path('line_chart_json', views.line_chart_json, name='line_chart_json'),
]
