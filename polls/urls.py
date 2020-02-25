from django.http import HttpRequest
from django.urls import path
from . import views
from . import data

urlpatterns = [
    path('', views.main_page, name='index'),
    path('poll_json/<str:start_date>/<str:end_date>/<str:candidates>', 
        views.poll_json_view, name='poll_json'),
    path('poll_json', views.poll_json_view, name='poll_json_post'),
    path('cov_json/<str:start_date>/<str:end_date>/<str:candidates>/<str:series>', 
        views.cov_json_view, name='cov_json'),
    path('cov_json', views.cov_json_view, name='cov_json_post'),
    #path('correlation_matrix/<str:start_date>/<str:end_date>', views.correlation_view, name='correlation_view'),
    #path('correlation_matrix', views.correlation_view, name='correlation_view_post'),
    #path('gdelt_heatmap/<str:start_date>/<str:end_date>', views.gdelt_heatmap_view, name='gdelt_heatmap_view'),
    #path('gdelt_heatmap', views.gdelt_heatmap_view, name='gdelt_heatmap_view_post'),
    path('main_page', views.main_page, name='main_page'),
    path('candidate', views.candidate, name='candidate')
]