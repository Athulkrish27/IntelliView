from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views


urlpatterns = [
    path("",views.interview_home,name="interview_home"),
    path("attend_interview/<int:int_id>",views.attend_interview,name="attend_interview"),
    path("applicant_varification",views.applicant_varification,name="applicant_varification"),
    path("face_verification",views.face_verification,name="face_verification"),
    path("video_feed",views.video_feed,name="video_feed"),
    path("capture_image",views.capture_image,name="capture_image"),
    path("session2",views.session2,name="session2"),
    path("introduce_yourself",views.introduce_yourself,name="introduce_yourself"),
    path("session3",views.session3,name="session3"),


]