from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from main.services import get_product, save_state
from .models import Product, ProductState, ProductTracking
from .serializers import (ProductSerializer,
                          ProductStateSerializer,
                          CardTrackingSerializer
                          )


class ProductView(ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.all()

    def create(self, request):
        data = get_product(request.data.get('code'))
        if not data:
            return Response({'Not Found': 'Нет данных'})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"Success": data})


class ProductStateView(ModelViewSet):
    serializer_class = ProductStateSerializer
    queryset = ProductState.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request):
        code = request.data.get('code')
        product = Product.objects.get(pk=code)
        if not product:
            return Response({"Bad Request": 'Продукт не найден'},)
        data = save_state(product.code, product.id)
        return Response({"Success": data})


class TrackingView(ModelViewSet):
    serializer_class = CardTrackingSerializer
    queryset = ProductTracking.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
