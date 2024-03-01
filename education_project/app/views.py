from django.shortcuts import render
from django.db.models import F, Q, Sum, Func
from models import *

#  todo
free_groups = Education.objects.prefetch_related("course").filter(maxlisteners__gte=Func(F("id"), function="COUNT"))
