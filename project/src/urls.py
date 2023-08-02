from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("create_account/", views.create_account, name="create_account"),
    path("logged/", views.logged, name="logged"),
    path("login/", views.login_func, name="login"),
    path("logout/", views.logout_func, name="logout"),
    path("send_message/", views.send_message, name="send_message"),
    path("admin/", views.admin, name="admin"),
    path("view_messages/", views.view_messages, name="view_messages"),
    path("delete_messages/", views.delete_messages, name="delete_messages"),
]
