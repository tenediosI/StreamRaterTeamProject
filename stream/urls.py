# -*- coding: utf-8 -*-

# from django.conf.urls import url

from stream import views
from django.urls import path


app_name = 'stream'

"""
Some URL's have a slash before them because at some point they stopped being recognized.
Even after looking into it with the help of tutors and demonstrators we couldn't figure it out.
These problems persist on python anywhere but non of the webpages with slashes before them work.
"""

urlpatterns = [

    path('', views.homepage, name='homepage'),
    path('<slug:category_name_slug>/',
         views.show_category, name='show_category'),
    path('<slug:category_name_slug>/<name>',
         views.show_streamer, name='show_streamer'),
    path('<slug:category_name_slug>/<name>/comment/', views.add_comment, name='add_comment'),
    path('<slug:category_name_slug>/<name>/<id>/discuss/', views.add_sub_comment, name='add_sub_comment'),
    path('/register/', views.register, name='register'),
    path('/about/', views.about, name='about'),
    path('/login/', views.user_login, name='login'),
    path('/edit_profile/', views.edit_profile, name='edit_profile'),
    path('/<username>/', views.view_profile, name='view_profile'),
    path('/logout/', views.user_logout, name='logout'),

]
