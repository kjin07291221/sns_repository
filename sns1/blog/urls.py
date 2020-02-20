from django.urls import path

from . import views



app_name = 'blog'



urlpatterns = [

    path('', views.PostList.as_view(), name='list'),
    path('detail/', views. PostDetail.as_view(), name='detail'),

    #path('category/<int:pk>/', views.PostCategoryList.as_view(), name='category'),
    #path('archive/<int:year>/', views.PostYearList.as_view(), name='year'),
    #path('archive/<int:year>/<int:month>/', views.PostMonthList.as_view(), name='month'),
    path('search/', views.PostSearchList.as_view(), name='search'),

    #path('comment/create/<int:pk>/', views.CommentCreate.as_view(), name='comment_create'),
    #path('reply/create/<int:pk>/', views.ReplyCreate.as_view(), name='reply_create'),
]
