from rest_framework import serializers

from .models import Product, ProductState, ProductTracking, TRACK_CHOICES


class ProductStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductState
        fields = ('code', 'product_name', 'current_price',
                  'old_price', 'brand', 'supplier')


class ProductSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    code = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('code', 'user',)


class CardTrackingSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    interval = serializers.ChoiceField(choices=TRACK_CHOICES)

    class Meta:
        model = ProductTracking
        fields = ('user', 'product', 'start_tracking', 'end_tracking', 'interval')
