from typing import Optional, Union
from rest_framework import status
from django.db.transaction import atomic
from django.db.models import Count, Value, Subquery, F
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from .models import *
from .serializers import EducationSerializer, OutputMultiModelSerializer, StudyingPlanSerializer


PAGE_SIZE = 10


class Logic:
    @staticmethod
    def get_student(id_) -> Optional[Student]:
        student = Student.objects.filter(student_id=id_)
        if student.count():
            return student[0]

    @staticmethod
    def check_payment(student_id) -> bool:
        """ Здесь возможна логика проверки квитанции """
        # todo
        payment = Contract.objects.filter(student_studentid=student_id)
        if payment.count():
            return True
        return False

    @staticmethod
    def get_or_create_group_and_get_course(return_group=False, return_course=False) -> Optional[Union[Group, Course]]:
        if not any([return_course, return_group]) or all([return_course, return_group]):
            raise ValueError
        queryset = Education.objects.select_related("course").select_related("group")\
            .values("course_id", "course__name", "course__maxlisteners", "course__minlisteners", "course__startat")\
            .exclude(course__startat__lte=timezone.now())\
            .annotate(current_listeners_count=Count("id", distinct=True))\
            .exclude(course__maxlisteners__lte=Value("current_listeners_count")).order_by("-current_listeners_count")
        if return_group:
            if queryset.count():
                return Group.objects.get(groupid=queryset[0].group_id)
            return Group.objects.create()
        if queryset.count():
            return Course.objects.get(course_id=queryset[0].course_id)


class Paginator(PageNumberPagination):
    page_size = PAGE_SIZE - 1
    max_page_size = PAGE_SIZE


class AvailableCourses(ListAPIView):
    http_method_names = ("get",)
    renderer_classes = (JSONRenderer,)
    serializer_class = OutputMultiModelSerializer
    pagination_class = Paginator

    def get_queryset(self):
        queryset = Education.objects.select_related("course").select_related("group")\
            .values("course_id", "course__name", "course__maxlisteners", "course__startat")\
            .exclude(course__startat__lte=timezone.now())\
            .annotate(current_listeners_count=Count("id", distinct=True))\
            .exclude(course__maxlisteners__lte=Value("current_listeners_count"))\
            .annotate(lessons_count=Count("", filter=Subquery(Lesson.objects.filter(product_id=F("course_id"))), distinct=True)  # todo: fixit
                      ).order_by("-current_listeners_count")
        return queryset


class AddStudent(CreateAPIView, Logic):
    serializer_class = EducationSerializer
    http_method_names = ("post",)
    renderer_classes = (JSONRenderer,)

    @atomic
    def create(self, request, *args, **kwargs):
        student_id = kwargs["studentid"]
        student = self.get_student(student_id)
        if not student:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not self.check_payment(student_id):
            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)
        group = self.get_or_create_group_and_get_course(return_group=True)
        request.data.update({"group": group.groupid})
        return super().create(request, *args, **kwargs)


class EducationPlan(ListAPIView, Logic):
    serializer_class = StudyingPlanSerializer
    renderer_classes = (JSONRenderer,)
    http_method_names = ("get",)

    def get_queryset(self):
        return Lesson.objects.prefetch_related("product")\
            .values("course_id", "course__name", "lesson__name")\
            .filter(course_id=self.request.course_id)

    def get(self, request, *args, **kwargs):
        student_id = kwargs["studentid"]
        if not self.get_student(student_id):
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not self.check_payment(student_id):
            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)
        if not Course.objects.filter(courseid=kwargs["courseid"]).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        request.course_id = kwargs["courseid"]
        return super().get(request, *args, **kwargs)
