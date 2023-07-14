from rest_framework.serializers import ModelSerializer
from .models import *
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email','otp', 'phone','first_name', 'last_name', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user



class ProductSerializer(ModelSerializer):
    class Meta:
        model=Product
        fields="__all__"

class UpdateProductSerializer(ModelSerializer):
    class Meta:
        model=Product
        fields="__all__"

class CategorySerializer(ModelSerializer):
    class Meta:
        model=Category
        fields="__all__"

class UpdateCategorySerializer(ModelSerializer):
    class Meta:
        model=Category
        fields="__all__"


class ProductSerialize1r(serializers.Serializer):
    product = serializers.IntegerField()
    quantity = serializers.IntegerField()

class CartSerializer(serializers.Serializer):
    products = ProductSerialize1r(many=True)
    class Meta:
        model=Cart
        exclude = ['user']

class UpdateCartSerializer(ModelSerializer):
    class Meta:
        model=Cart
        exclude = ['user']

class UserList(ModelSerializer):
    class Meta:
        model=User
        fields=['username']

class ProductList(ModelSerializer):
    class Meta:
        model=Product
        fields=['name','price','discription']
    
class ProductSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'discription', 'seller')

class CartItemSerializer1(serializers.ModelSerializer):
    product = ProductSerializer1()

    class Meta:
        model = CartItem
        fields = ('product', 'product_quantity', 'total_bill', 'product_seller')

class CartListSerializer(serializers.ModelSerializer):
    user = UserList()
    cart_items = CartItemSerializer1(source="cart_items.all",many=True)

    class Meta:
        model = Cart
        fields = ('id', 'user', 'cart_items', 'total_bill')



class DeliveryDetailsSerializer(ModelSerializer):
    class Meta:
        model=DeliveryDetails
        exclude = ['user']

class UpdateDeliveryDetailsSerializer(ModelSerializer):
    class Meta:
        model=DeliveryDetails
        exclude = ['user']


class MyTokenObtainPairSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        return data


class UserBankDetailsSerializer(ModelSerializer):
    class Meta:
        model=UserBankDetails
        exclude = ['user']
        
class UpdateUserBankDetailsSerializer(ModelSerializer):
    class Meta:
        model=UserBankDetails
        exclude = ['user']

class OrderSerializer(ModelSerializer):
    class Meta:
        model=Order
        fields="__all__"