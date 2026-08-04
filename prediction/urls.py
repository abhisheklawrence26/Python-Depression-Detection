from django.urls import path
from . import views
from prediction import views as prediction_views
from django.views.generic import RedirectView
urlpatterns = [
    path("", RedirectView.as_view(url="/login/"), name="home"),
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("quiz/", views.quiz, name="quiz"),
    path("result/", views.result, name="result"),

    path("face/", views.face, name="face"),
    path("analyze-face/", views.analyze_face, name="analyze_face"),
    path("save-face-result/", views.save_face_result, name="save_face_result"),

    path("journal/", views.journal, name="journal"),

    path("hospital/", views.hospital_page, name="hospital"),
    path("nearby-hospitals/", views.nearby_hospitals, name="nearby_hospitals"),

    path("information/", views.information, name="information"),
]






