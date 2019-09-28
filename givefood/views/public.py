from datetime import date
import operator
from collections import OrderedDict

from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.cache import cache_page
from django.shortcuts import redirect
from django.http import HttpResponse, Http404

from givefood.models import Foodbank, Order, FoodbankChange
from givefood.func import get_image, item_class_count
from givefood.const.item_classes import TOMATOES, RICE, PUDDINGS, SOUP, FRUIT, MILK


@cache_page(60*15)
def public_index(request):

    total_weight = 0
    total_calories = 0
    total_items = 0

    orders = Order.objects.all()
    for order in orders:
        total_weight = total_weight + order.weight
        total_calories = total_calories + order.calories
        total_items = total_items + order.no_items

    total_weight = float(total_weight) / 1000000
    total_calories = float(total_calories) / 1000000

    no_foodbanks = len(Foodbank.objects.all())

    template_vars = {
        "no_foodbanks":no_foodbanks,
        "total_weight":total_weight,
        "total_calories":total_calories,
        "total_items":total_items,
    }
    return render_to_response("public/index.html", template_vars)


def public_annual_report(request, year):

    year = int(year)
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)

    total_weight = float(0)
    total_calories = 0
    total_items = 0
    items = {}

    foodbanks = Foodbank.objects.all()
    no_foodbanks = len(Foodbank.objects.all())

    orders = Order.objects.filter(delivery_date__gte = year_start, delivery_date__lte = year_end)

    for order in orders:
        total_weight = total_weight + order.weight
        total_calories = total_calories + order.calories
        total_items = total_items + order.no_items

        for line in order.lines():
            if line.name in items:
                items[line.name] = items.get(line.name) + line.quantity
            else:
                items[line.name] = line.quantity

    total_weight = total_weight / 1000

    tinned_tom = item_class_count(items, TOMATOES)
    rice = item_class_count(items, RICE)
    rice = float(rice) / 1000
    tinned_pud = item_class_count(items, PUDDINGS)
    soup = item_class_count(items, SOUP)
    fruit = item_class_count(items, FRUIT)
    milk = item_class_count(items, MILK)

    calorie_days = total_calories / 2000
    calorie_years = float(calorie_days / 365)

    template_vars = {
        "year":year,
        "total_weight":int(total_weight),
        "total_calories":total_calories,
        "total_items":total_items,
        "calorie_days":calorie_days,
        "calorie_years":calorie_years,
        "tinned_tom":tinned_tom,
        "rice":rice,
        "tinned_pud":tinned_pud,
        "soup":soup,
        "fruit":fruit,
        "milk":milk,
        "foodbanks":foodbanks,
        "no_foodbanks":no_foodbanks,
    }
    return render_to_response("public/annual_report.html", template_vars)


@cache_page(60*60)
def public_product_image(request):

    delivery_provider = request.GET.get("delivery_provider")
    product_name = request.GET.get("product_name")

    url = get_image(delivery_provider,product_name)

    return redirect(url)


def distill_webhook(request):

    new_foodbank_change = FoodbankChange(
        post_text = request.POST,
    )
    new_foodbank_change.save()

    return HttpResponse("OK")
