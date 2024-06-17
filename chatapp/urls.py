from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("mockgpt", views.mockgpt, name="mockgpt"),
    path("signup", views.signup, name="signup"),
    path("signin", views.signin, name="signin"),
    path("signout", views.signout, name="signout"),
    path("info/", views.info, name="info"),
    path("mock/", views.mock, name="mock"),
    path("mock/test", views.test, name="test"),
    path("identity/", views.identity, name="identity"),
    path("identity/edit_resume", views.edit_resume, name="edit"),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
