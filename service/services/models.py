from django.core.validators import MaxValueValidator
from django.db import models

from clients.models import Client
from services.tasks import set_price


class Service(models.Model):
    name = models.CharField(max_length=50)
    full_price = models.PositiveIntegerField()

    def __str__(self):
        return f'Service: {self.name}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__full_price = self.full_price

    def save(self, *args, **kwargs):
        if self.full_price != self.__full_price:
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)

        return super().save(*args, **kwargs)


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

    # при создании плана таска все равно будет запускаться
    # а нужно сделать так, чтобы она запускалась ТОЛЬКО при изменении плана
    # поэтому: переопределим инициализацию модели
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__discount = self.discount
    # в момент ее инициализации нужно зафиксировать пару значений

    # сохранять будем тут, т.к. от ПЛАНА могут зависеть несколько подписок
    def save(self, *args, **kwargs):
        #                       related_name для плана (из подписки)
        if self.discount != self.__discount:
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)

        return super().save(*args, **kwargs)


class Subscription(models.Model):
    # related_name - под каким именем будет доступна внутри модели с которой создаем связь Client
    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.PROTECT)
    price = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Sub - Client: {self.client}, Service: {self.service}, Plan: {self.plan}'
