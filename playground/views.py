from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, F
from django.db import transaction, connection
from django.db.models import Count, Min, Max, Avg, Sum, Value, Func, ExpressionWrapper, DecimalField
from django.db.models.functions import Concat
from store.models import Product, Customer, Collection, Order, OrderItem
from tags.models import TaggedItem


def say_hello(request):
    # return render(request, "hello.html", {"name": "Arafat"})
    return HttpResponse("Hello World")
