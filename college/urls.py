from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views


urlpatterns = [
    path("",views.college_home,name="college_home"),
    path("career_page",views.career_page,name="career_page"),
    path("submit_application",views.submit_application,name="submit_application"),
    path("apply_interview/<str:interview_id>",views.apply_interview,name="apply_interview"),
    path("collect_email/<str:interview_id>",views.collect_email,name="collect_email"),
    path("send_otp",views.send_otp,name="send_otp"),
    path("verify_otp",views.verify_otp,name="verify_otp"),

]
