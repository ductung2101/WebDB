from django.urls import path

from . import views

urlpatterns = [
    path('', views.main_page, name='index'),
    path('sub', views.sub, name='sub'),
    path('line_chart', views.line_chart, name='line_chart'),
    path('line_chart_json', views.line_chart_json, name='line_chart_json'),
    path('poll_json/<str:start_date>/<str:end_date>', views.poll_json, name='poll_json'),
    path('poll_json', views.poll_json, name='poll_json_post'),
    path('correlation_matrix', views.corMatix, name='correlation_matrix'),
    # path('influence_json', views.influence_json, name='influence_json'),
    path('main_page', views.main_page, name='main_page'),
]
