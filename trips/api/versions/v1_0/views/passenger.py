from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.exceptions import APIException
from oauth2_provider.contrib.rest_framework.permissions import TokenMatchesOASRequirements
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from project.mixins import PrefetchQuerysetModelMixin, PatchModelMixin
from ..inspectors import DjangoFilterDescriptionInspector
from ..filters import LocalizedOrderingFilter
from ..serializers import PassengerTripListRetrieveSerializer, PassengerActionsSerializer
from .....models import Trip
from .....exceptions import PassengerDeniedError, PassengerNotBookedError


class PassengerTripViewset(
        PrefetchQuerysetModelMixin,
        PatchModelMixin,
        viewsets.ReadOnlyModelViewSet):
    """Viagens

    """
    # Only allow trips in the future
    swagger_tags = ['Passageiro']
    queryset = Trip.objects.all()
    max_limit = 50
    limit = 10
    filter_backends = (
        LocalizedOrderingFilter,
    )
    ordering_fields = [
        'datetime', 'price'
    ]
    ordering = ['-datetime', 'price']
    serializer_class = PassengerTripListRetrieveSerializer
    # permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["trips:passenger:read"]],
        "PATCH": [["trips:passenger:write"]],
    }

    def get_queryset(self):
        qs = super().get_queryset()
        # Only trips the user is a passenger
        qs = qs.filter(passengers__user__in=[self.request.user])
        # If the trip already happened, only allow GET
        if self.request.method != 'GET':
            qs = qs.filter(datetime__gt=timezone.now())
        return qs

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return PassengerActionsSerializer
        return super().get_serializer_class()

    @swagger_auto_schema(
        responses={
            400: "Seus parâmetros GET estão mal formatados",
            404: "Carona pesquisada não existe"
        },
        manual_parameters=[
            openapi.Parameter('fields', openapi.IN_QUERY,
                              "Seleciona dados retornados. Lista separada por vírgula dos campos a serem retornados. Campos aninhados são suportados. Exemplo: `fields=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING),
            openapi.Parameter('exclude', openapi.IN_QUERY,
                              "Exclui dados retornados. Lista separada por vírgula dos campos a serem excluídos. Campos aninhados são suportados. Exemplo: `exclude=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING)
        ],
        security=[
            {'unicaronas auth': ['trips:passenger:read']}
        ]
    )
    def retrieve(self, *args, **kwargs):
        """Detalhes de uma carona

        Permite acessar detalhes de caronas **que o usuário é passageiro**.

        Para acessar, use a ID de uma carona pesquisada.

        > **Dica:** Você também pode usar os parâmetros GET `fields` e `exclude` para filtrar os campos retornados pela API
        """
        return super().retrieve(*args, **kwargs)

    @swagger_auto_schema(
        responses={
            400: "Seus parâmetros GET estão mal formatados",
            # 200: PaginatedResponseSerializer
        },
        manual_parameters=[
            openapi.Parameter('fields', openapi.IN_QUERY,
                              "Seleciona dados retornados. Lista separada por vírgula dos campos a serem retornados. Campos aninhados são suportados. Exemplo: `fields=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING),
            openapi.Parameter('exclude', openapi.IN_QUERY,
                              "Exclui dados retornados. Lista separada por vírgula dos campos a serem excluídos. Campos aninhados são suportados. Exemplo: `exclude=campo1,campo2{sub_campo1, sub_campo2}`", type=openapi.TYPE_STRING)
        ],
        filter_inspectors=[DjangoFilterDescriptionInspector],
        security=[
            {'unicaronas auth': ['trips:read']}
        ]
    )
    def list(self, *args, **kwargs):
        """Listar caronas

        Permite listar caronas que o usuário é passageiro.

        Esse endpoint suporta ordenação por `price` e por `datetime`.

        > **Dica:** Você também pode usar os parâmetros GET `fields` e `exclude` para filtrar os campos retornados pela API
        """
        return super().list(*args, **kwargs)

    @swagger_auto_schema(
        responses={
            404: 'Carona não existe, já aconteceu, ou você não tem permissão para acessá-la',
            400: 'A ação não é compatível com o estado do passageiro',
        },
        security=[
            {'unicaronas auth': ['trips:passenger:write']}
        ]
    )
    def partial_update(self, *args, **kwargs):
        """Ações do passageiro

        Permite que o passageiros realize ações em caronas que **ainda não aconteceram** e que **o usuário seja passageiro**. Caso contrário, a resposta desse endpoint será um erro *404*.

        Para acessar, use a ID de uma carona(`id`)

        As ações são enviadas por um parâmetro no *PATCH* chamado `action` e têm os seguintes efeitos:

        | Ação          | Atua em                   | Efeito                        |
        | ------------- |---------------------------|-------------------------------|
        | `give_up`     | Passageiros **pendentes** ou **aprovados**|Passageiro sai da carona|
        """
        return super().partial_update(*args, **kwargs)

    def perform_update(self, serializer):
        action = serializer.validated_data['action']
        passenger = serializer.instance
        trip = Trip.objects.get(id=self.kwargs['id'])
        action_map = {
            'give_up': trip.give_up,
        }
        try:
            return
            action_map[action](passenger.user)
        except PassengerDeniedError:
            raise APIException({'detail': 'Passageiros negados não podem desistir da carona'}, code=status.HTTP_400_BAD_REQUEST)
        except PassengerNotBookedError:
            raise APIException({'detail': 'Usuário não é passageiro da carona'}, code=status.HTTP_400_BAD_REQUEST)
