#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models
from django.template.defaultfilters import slugify

from const.general import DELIVERY_HOURS_CHOICES
from func import parse_order_text


class Foodbank(models.Model):

    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50, editable=False)
    address = models.TextField()
    latt_long = models.CharField(max_length=50, verbose_name="Latt,Long")

    contact_email = models.EmailField()
    notification_email = models.EmailField()
    phone_number = models.CharField(max_length=20)

    url = models.URLField(max_length=200, verbose_name="URL")
    shopping_list_url = models.URLField(max_length=200, verbose_name="Shopping list URL")

    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    last_order = models.DateField(editable=False,null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Foodbank, self).save(*args, **kwargs)


class Order(models.Model):

    order_id = models.CharField(max_length=50, editable=False)
    foodbank = models.ForeignKey(Foodbank)
    items_text = models.TextField()

    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    delivery_date = models.DateField()
    delivery_hour = models.IntegerField(choices=DELIVERY_HOURS_CHOICES)
    delivery_datetime = models.DateTimeField(editable=False)

    weight = models.PositiveIntegerField(editable=False)
    calories = models.PositiveIntegerField(editable=False)
    cost = models.PositiveIntegerField(editable=False) #pence
    no_lines = models.PositiveIntegerField(editable=False)
    no_items = models.PositiveIntegerField(editable=False)

    def delivery_datetime(self):
        # calculate from delivery_date & delivery_hour
        pass

    def save(self, *args, **kwargs):
        # Generate ID
        self.order_id = "gf-%s-%s" % (self.foodbank.slug,str(self.delivery_date))
        # Store delivery_datetime
        self.delivery_datetime = datetime(
            self.delivery_date.year,
            self.delivery_date.month,
            self.delivery_date.day,
            self.delivery_hour,
            0,
        )
        # Order counts
        order_weight = 0
        order_calories = 0
        order_cost = 0
        no_lines = 0
        no_items = 0

        order_lines = parse_order_text(self.items_text)

        for order_line in order_lines:
            no_lines += 1
            no_items += order_line.get("quantity")

            line_weight = order_line.get("weight") * order_line.get("quantity")
            order_weight = order_weight + line_weight

            if order_line.get("calories"):
                line_calories = (order_line.get("weight") / 100) * order_line.get("calories")
                order_calories = order_calories + line_calories

            line_cost = order_line.get("item_cost") * order_line.get("quantity")
            order_cost = order_cost + line_cost

        self.weight = order_weight
        self.calories = order_calories
        self.cost = order_cost
        self.no_lines = no_lines
        self.no_items = no_items



        super(Order, self).save(*args, **kwargs)

        # Delete all the existing orderlines
        OrderLine.objects.filter(order = self).delete()

        for order_line in order_lines:

            line_weight = order_line.get("weight") * order_line.get("quantity")

            if order_line.get("calories"):
                line_calories = (order_line.get("weight") / 100) * order_line.get("calories")

            line_cost = order_line.get("item_cost") * order_line.get("quantity")

            new_order_line = OrderLine(
                foodbank = self.foodbank,
                order = self,
                name = order_line.get("name"),
                quantity = order_line.get("quantity"),
                item_cost = order_line.get("item_cost"),
                line_cost = line_cost,
                weight = line_weight,
                calories = order_line.get("calories"),
            )
            new_order_line.save()

    def lines(self):
        return OrderLine.objects.filter(order = self)


class OrderLine(models.Model):

    foodbank = models.ForeignKey(Foodbank)
    order = models.ForeignKey(Order)

    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    item_cost = models.PositiveIntegerField() #pence
    line_cost = models.PositiveIntegerField()

    weight = models.PositiveIntegerField(editable=False,null=True)
    calories = models.PositiveIntegerField(editable=False,null=True)
