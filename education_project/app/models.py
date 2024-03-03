from random import randint
from uuid import uuid4
from django.utils import timezone
from django.db import models
from django.core.validators import RegexValidator
from djmoney.models.fields import MoneyField


MIN_LISTENERS = 10
MAX_LISTENERS = 50


def get_uuid():
    return str(uuid4())


def get_random_start_date():
    return timezone.now() + timezone.timedelta(days=randint(1, 32))


class Course(models.Model):
    courseid = models.AutoField(primary_key=True)
    author = models.ForeignKey("Author", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=70, unique=True)
    startat = models.DateTimeField(default=get_random_start_date)
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    minlisteners = models.PositiveSmallIntegerField(default=MIN_LISTENERS)
    maxlisteners = models.PositiveSmallIntegerField(default=MAX_LISTENERS)

    def __str__(self):
        return f"{self.name} ({str(self.author)})"


class Contract(models.Model):
    id = models.UUIDField(default=get_uuid, primary_key=True)
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    transactionid = models.CharField(max_length=12, validators=[RegexValidator(regex=r"\d{3}-\d{3}-\d{3}")])
    isactive = models.BooleanField(default=True)


class Author(models.Model):
    id = models.UUIDField(default=get_uuid, primary_key=True)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class Lesson(models.Model):
    lessonid = models.UUIDField(default=get_uuid, primary_key=True)
    product = models.ForeignKey("Course", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    videourl = models.URLField()


class Group(models.Model):
    groupid = models.UUIDField(default=get_uuid, primary_key=True)
    name = models.CharField(max_length=150)


class Student(models.Model):
    studentid = models.UUIDField(default=get_uuid, primary_key=True)
    groupid = models.UUIDField(default=get_uuid)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)


class Education(models.Model):
    id = models.UUIDField(default=get_uuid, primary_key=True)
    course = models.ForeignKey("Course", models.CASCADE)
    group = models.ForeignKey("Group", models.CASCADE)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
