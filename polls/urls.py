from django.http import HttpRequest
from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='index'),
    path('sub', views.sub, name='sub'),
    path('poll_json/<str:start_date>/<str:end_date>', views.poll_json_view, name='poll_json'),
    path('poll_json', views.poll_json_view, name='poll_json_post'),
    path('correlation_matrix/<str:start_date>/<str:end_date>', views.correlation_view, name='correlation_view'),
    path('correlation_matrix', views.correlation_view, name='correlation_view_post'),
    # path('influence_json', views.influence_json, name='influence_json'),
    path('main_page', views.main_page, name='main_page'),
]
