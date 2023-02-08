from django.core.validators import MaxValueValidator
from django.db import models

from clients.models import Client


class Service(models.Model):
    name = models.CharField(max_length=50)
    full_price = models.PositiveIntegerField()

    def __str__(self):
        return f'Service: {self.name}'


class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount')
    )
    plan_type = models.CharField(max_length=10, choices=PLAN_TYPES)
    discount = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])

    def __str__(self):
        return f'Plan: {self.plan_type}'


class Subscription(models.Model):
    # related_name - под каким именем будет доступна внутри модели с которой создаем связь Client
    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.PROTECT)

    def __str__(self):
        return f'Sub - Client: {self.client}, Service: {self.service}, Plan: {self.plan}'

