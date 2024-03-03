from django.urls import path
from .views import EducationPlan, AddStudent, AvailableCourses


urlpatterns = [
    path(r"upstudy/?P<studentid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/?P<courseid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/", AddStudent.as_view()),
    path("studying/", AvailableCourses.as_view()),
    path(r"plan/?P<studentid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/?P<courseid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/", EducationPlan.as_view())
]
