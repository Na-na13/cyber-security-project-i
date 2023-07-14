from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("create_account/", views.create_account, name="create_account"),
    path("logged/", views.logged, name="logged"),
    path("login/", views.login_func, name="login"),
    path("logout/", views.logout_func, name="logout"),
    path("send_message/", views.send_message, name="send_message")
]
