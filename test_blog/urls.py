from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from blog.views import (main, sign_up, CustomLoginView, PostListView, PostFormView, PostUpdateView, PostDeleteView,
                        new_comment_leave, unsubscribe_view, logout_view)

from blog.ui_views import PostsListUIView, PostUIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include([
        path('', PostsListUIView.as_view(), name='ui_posts_list'),
        path('post/<slug:slug>/<int:pk>', PostUIView.as_view(), name='ui_post'),
    ])),
    path('uviyti', CustomLoginView.as_view(), name='login'),
    path('logout', logout_view, name='logout'),
    path('sign-up', sign_up, name='sign_up'),
    path('ckeditor/', include('ckeditor_uploader.urls')),

    path('admin-panel/', include([
        path('', main, name='index'),
        path('posts-list', PostListView.as_view(), name='posts-list'),
        path('post-add', PostFormView.as_view(), name='post-add'),
        path('post-edit/<slug:slug>/<int:pk>', PostUpdateView.as_view(), name='post-edit'),
        path('post-delete/<slug:slug>/<int:pk>', PostDeleteView.as_view(), name='post-delete'),
    ])),

    path('test_url/', new_comment_leave, name='new_comment'),
    path('unsubscribe/<uidb64>/<token>', unsubscribe_view, name='unsubscribe'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
