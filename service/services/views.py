from django.db.models import Prefetch, F, Sum
from rest_framework.viewsets import ReadOnlyModelViewSet

from clients.models import Client
from services.models import Subscription
from services.serializers import SubscriptionSerializer


class SubscriptionView(ReadOnlyModelViewSet):
    queryset = Subscription.objects.all().prefetch_related(
        'plan',
        Prefetch('client', queryset=Client.objects.all().select_related('user').only('company_name', 'user__email'))
    ).annotate(price=F('service__full_price') -
                     F('service__full_price') * F('plan__discount') / 100.00)
    # теперь в queryset каждый результат будет дополнен именем price
    # .annotate - вычисления на уровне БД, чтобы не добавлять еще один prefetch
    # у каждой подписки появится вирутальное поле price как и в случае с SerializerMethodField()
    # F - функция, с помощью которой обраащемся к полям

    serializer_class = SubscriptionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)

        response_data = {'result': response.data}
        # используем виртуальную переменную price и высчитываем сумму и кладем в переменую total
        response_data['total_amount'] = queryset.aggregate(total=Sum('price')).get('total')
        response.data = response_data

        return response
