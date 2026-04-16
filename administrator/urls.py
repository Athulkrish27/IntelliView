from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views


urlpatterns = [
    path("",views.admin_home,name="admin_home"),
    path("admin_home",views.admin_home,name="admin_home"),
    path("admin_login/",views.admin_login,name="admin_login"),
    path("admin_logout/",views.admin_logout,name="admin_logout"),
    path("create_interview",views.create_interview,name="create_interview"),
    path("view_interview",views.view_interview,name="view_interview"),
    path("add_syllabus",views.add_syllabus,name="add_syllabus"),
    path("view_syllabus",views.view_syllabus,name="view_syllabus"),
    path("syllabus_action/<str:syl_id>",views.syllabus_action,name="syllabus_action"),
    path("generate_qa",views.generate_qa,name="generate_qa"),
    path("manage_qa/<str:qa_id>",views.manage_qa,name="manage_qa"),
    path("update_interview/<int:int_id>",views.update_interview,name="update_interview"),
    path("edit_interview/<int:int_id>",views.edit_interview,name="edit_interview"),
    path("add_syl_interview_map/<int:int_id>",views.add_syl_interview_map,name="add_syl_interview_map"),
    path("remove_syl_interview_map/<int:int_id>",views.remove_syl_interview_map,name="remove_syl_interview_map"),
    path("cancel_interview/<int:int_id>",views.cancel_interview,name="cancel_interview"),
    path("start_interview/<int:int_id>",views.start_interview,name="start_interview"),
    path("finish_interview/<int:int_id>",views.finish_interview,name="finish_interview"),
    path("see_result/<int:int_id>",views.see_result,name="see_result"),
    path("select_candidate/<int:app_id>",views.select_candidate,name="select_candidate")
]