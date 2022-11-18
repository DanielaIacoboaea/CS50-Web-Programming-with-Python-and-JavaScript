
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("following", views.following, name="following"),
    path("<int:user_id>", views.profile, name="profile"),
    path("likes/<int:post_id>", views.likes, name="likes"),
    path("comments", views.comments, name="comments"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
