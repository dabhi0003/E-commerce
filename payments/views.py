from django.shortcuts import render,redirect
from django.views.generic.base import TemplateView
from django.conf import settings
import stripe
from .serializers import *
from .models import *
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework import status
import random



def generate_otp():
    digits = "0123456789"
    otp = ""

    for _ in range(6): 
        otp += random.choice(digits)

    return otp

class CreateUserView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.user.is_superuser:
            user = serializer.save()

            if request.data.get('role') == 'admin':
                user.role = 'admin'

            if request.data.get('role') == 'seller':
                user.role = 'seller'

            else:
                user.role = 'common'
            user.otp = generate_otp()
            user.save()
            return Response({
                # "user": UserSerializer(user, context=self.get_serializer_context()).data
                "Your Otp": user.otp,
                "message": "Successfully Created Account."
            })
        
class VerifyPhoneNumberView(APIView):
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')
        try:
            user = User.objects.get(phone=email, otp=otp)
            user.phone_varified = True
            user.save()
            return Response("Phone number verified successfully.",200)
        except User.DoesNotExist:
            return Response("Invalid email or OTP.", 400) 


class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    def validate(self,request, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        return data

class CategoryView(APIView):
    def post(self,request):
        user=request.user

        if user.is_anonymous or not hasattr(user, 'role'):
            return Response("Authentication credentials not provided or invalid.", status=400)

        if user.role == "admin":
            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=400)
        else:
            return Response("Only admin can add the category.", status=400)
        
    def get(self,request):

        if request.user.is_anonymous or not hasattr(request.user, 'role'):
            return Response("Authentication credentials not provided or invalid.", status=400)

        if request.user.role=="admin" or request.user.role=="seller":
            category=Category.objects.all()
            serilizer=CategorySerializer(instance=category,many=True)
            return Response(serilizer.data) 
        else:
            return Response("Only Admin or seller can show the data.")
        

    def put(self,request,id):
        if request.user.is_anonymous or not hasattr(request.user, 'role'):
            return Response("Authentication credentials not provided or invalid.", status=400)
        
        if request.user.role=="admin" or request.user.role=="seller":
            category=Category.objects.get(id=id)
            serilizer=UpdateCategorySerializer(data=request.data,instance=category,partial=True)
            if serilizer.is_valid():
                serilizer.save()
                return Response(serilizer.data)
            else:
                return Response(serilizer.errors,status=400)
        else:
            return Response("Only Admin and seller can update the data.")

class ProductView(APIView):
    def post(self,request):
        if request.user.is_anonymous or not hasattr(request.user, 'role'):
            return Response("Authentication credentials not provided or invalid.", status=400)
        
        if request.user.role == "seller":
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(seller=request.user)
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=400)
        else:
            return Response("Only admin and seller can add the Product.", status=400)
        

    def get(self,request):
        if request.user.is_anonymous or not hasattr(request.user, 'role'):
            return Response("Authentication credentials not provided or invalid.", status=400)
        
        if request.user.role=="admin" or request.user.role=="seller":
            product=Product.objects.all()
            serilizer=ProductSerializer(instance=product,many=True)
            return Response(serilizer.data) 
        else:
            return Response("Only Admin can show the data.")
    
    def put(self,request,id):
        if request.user.is_anonymous or not hasattr(request.user, 'role'):
            return Response("Authentication credentials not provided or invalid.", status=400)
        
        if request.user.role=="admin" or request.user.role=="seller":
            product=Product.objects.get(id=id)
            serilizer=UpdateProductSerializer(data=request.data,instance=product,partial=True)
            if serilizer.is_valid():
                serilizer.save()
                return Response(serilizer.data)
            else:
                return Response("Invalid Data")
        else:
            return Response("only admin or seller can update the poduct")
        
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_anonymous or not hasattr(request.user, 'role'):
            return Response("Authentication credentials not provided or invalid.", status=status.HTTP_400_BAD_REQUEST)

        if request.user.role != "common":
            return Response("Only common User can buy a product", status=status.HTTP_400_BAD_REQUEST)

        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            products = serializer.validated_data.get('product')
            quantity = int(serializer.validated_data.get('product_quantity'))

            cart, created = Cart.objects.get_or_create(user=request.user)

            total_bill = 0
            product=None

            for product in products:
                product_id = product.id
                product_obj = get_object_or_404(Product, id=product_id)
                product_price = int(product_obj.price)
                product_seller = product_obj.seller

                cart.product.add(product_obj)

                total_bill += product_price * quantity

            cart.total_bill = total_bill
            cart.save()

            return Response("Products Added to Your Cart", status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_anonymous or not hasattr(request.user, 'role'):
            return Response("Authentication credentials not provided or invalid.", status=400)

        if request.user.role == "common":
            serializer = CartSerializer(data=request.data)
            if serializer.is_valid():
                products_data = serializer.validated_data.get('products')

                cart = Cart.objects.create(user=request.user)
                total_bill = 0

                for product_item in products_data:
                    product_id = product_item['product']
                    quantity = product_item['quantity']

                    try:
                        product = Product.objects.get(pk=product_id)
                    except Product.DoesNotExist:
                        return Response(f"Product with id {product_id} does not exist.", status=400)

                    seller = product.seller
                    price = product.price
                    bill = int(price) * int(quantity)
                    total_bill += bill

                    cart_item = CartItem.objects.create(
                        cart=cart,
                        product=product,
                        product_quantity=quantity,
                        product_seller=seller,
                        total_bill=bill
                    )

                cart.total_bill = total_bill
                cart.product_quantity=quantity
                cart.product_seller=seller
                cart.save()

                return Response("Products added to your cart.")
            else:
                return Response(serializer.errors, status=400)
        else:
            return Response("Only common users can buy a product.", status=400)


    def get(self,request):
        if request.user.is_anonymous or not hasattr(request.user, 'role'):
            return Response("Authentication credentials not provided or invalid.", status=400)
        
        user=request.user
        if request.user.role=="admin":
            details=Cart.objects.all()
            serilizer=CartListSerializer(instance=details,many=True)
            return Response(serilizer.data) 
        details=Cart.objects.filter(user=user)
        serializer=CartListSerializer(instance=details,many=True)
        return Response(serializer.data)


    def put(self,request,id):
        if request.user.is_anonymous or not hasattr(request.user, 'role'):
            return Response("Authentication credentials not provided or invalid.", status=400)
        
        if request.user.role=="common":
            product=Cart.objects.get(id=id)
            serilizer=UpdateCartSerializer(data=request.data,instance=product,partial=True)
            if serilizer.is_valid():
                product = serilizer.validated_data.get('product')
                quantity = serilizer.validated_data.get('product_quantity')
                price = product.price
                bill=int(price)*int(quantity)
                serilizer.save(user=request.user,total_bill=bill)
                return Response(serilizer.data)
            else:
                return Response("Invalid Data")
        else:
            return Response("only coomon user can update the Cart")

class DeliveryDetailsView(APIView):
    def post(self,request):
        if request.user.is_anonymous or not hasattr(request.user, 'role'):
            return Response("Authentication credentials not provided or invalid.", status=400)
        user=request.user

        if request.user.role=="common":
            serializer=DeliveryDetailsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user)
                return Response(serializer.data)
            else:
                return Response("Invalid Data")
        else:
            return Response("Only Common User Can add this details")

    def get(self,request):
        if request.user.is_anonymous or not hasattr(request.user, 'role'):
            return Response("Authentication credentials not provided or invalid.", status=400)
        if request.user.role=="common":
            details=DeliveryDetails.objects.all()
            serializer=DeliveryDetailsSerializer(instance=details,many=True)
            return Response(serializer.data)
        else:
            return Response("Only common user can show details")
        

    def put(self,request,id):
        if request.user.is_anonymous or not hasattr(request.user, 'role'):
            return Response("Authentication credentials not provided or invalid.", status=400)
        
        if request.user.role=="common":
            product=DeliveryDetails.objects.get(id=id)
            serilizer=UpdateDeliveryDetailsSerializer(data=request.data,instance=product,partial=True)
            if serilizer.is_valid():
                serilizer.save()
                return Response(serilizer.data)
            else:
                return Response("Invalid Data")
        else:
            return Response("only coomon user can update the Cart")

class HomepageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["key"] = settings.STRIPE_PUBLISHABLE_KEY
        cart_id = 73
        cart = Cart.objects.get(id=cart_id)
        context["cart_items"] = cart.cart_items.all()
        context["total_bill"] = cart.total_bill
        return context
   

stripe.api_key = settings.STRIPE_SECRET_KEY

def ChargeView(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = request.POST.get("quantity")
        total_bill = request.POST.get("total_bill")



        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(f"Product with ID {product_id} does not exist.", status=400)

        seller = product.seller
        admin_amount = int(total_bill) * 0.15
        seller_amount = int(total_bill) - admin_amount

        metadata = {
            'admin_amount': int(admin_amount),
            'seller_amount': int(seller_amount),
            'seller': seller,
            'product': product.name
        }

        price = stripe.Price.create(
            unit_amount=int(product.price) * 100,
            currency='inr',
            product_data={
                'name': product.name
            }
        )

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price.id,
                    'quantity': int(quantity)
                }
            ],
            payment_intent_data={
                'metadata': metadata
            },
            mode='payment',
            success_url='http://127.0.0.1:8000/api/bill/',
            cancel_url='http://127.0.0.1:8000/api/charge/'
        )

        balance_transactions = stripe.BalanceTransaction.list(
                limit=1,
                expand=['data.source'],
                type='payment',
                payout=None
            )

        user=User.objects.filter(email=seller)
            
        for i in user:
                pass
        admin_bank_details = UserBankDetails.objects.get(user_type='admin')
        seller_bank_details = UserBankDetails.objects.get(user=i.id)
        a=int(admin_bank_details.account_balance)+int(admin_amount)
        b=int(seller_bank_details.account_balance)+int(seller_amount)
        admin_bank_details.account_balance=a
        seller_bank_details.account_balance=b
        admin_bank_details.save()
        seller_bank_details.save()
    
        user=Cart.objects.get(pk=73)
        print('user: ', user)
        order = Order.objects.create(
            user=user.user,
            product=product,
            seller=seller,
            price=product.price,
            quantity=quantity,
        )
        return redirect(session.url)

    return redirect("bill")

def Charge_allView(request):
    if request.method == "POST":
        cart_id = 73
        total_bill = int(request.POST.get("total_bill"))
        new_bill = int(total_bill / 2)
        cart_items = CartItem.objects.filter(cart=cart_id)
        admin_total = 0

        line_items = [] 

        for cart_item in cart_items:
            product = cart_item.product
            seller = product.seller
            item_total = int(cart_item.total_bill)
            admin_amount = item_total * 0.15
            seller_amount = item_total - admin_amount

            admin_total += admin_amount

            price = stripe.Price.create(
                unit_amount=int(cart_item.product.price) * 100,
                currency='inr',
                product_data={
                    'name': product.name
                }
            )

            line_item = {
                'price': price.id,
                'quantity': int(cart_item.product_quantity)
            }
            cart_user=Cart.objects.get(pk=73)
            order = Order.objects.create(
                user=cart_user.user,
                product=product,
                seller=seller,
                price=product.price,
                quantity=cart_item.product_quantity,
            )
            line_items.append(line_item)

            user = User.objects.filter(email=seller)

            for i in user:
                pass

            seller_bank_details = UserBankDetails.objects.get(user=i.id)
            b = int(seller_bank_details.account_balance) + int(seller_amount)
            seller_bank_details.account_balance = b
            seller_bank_details.save()

        admin_bank_details = UserBankDetails.objects.get(user_type='admin')
        a = int(admin_bank_details.account_balance) + int(admin_total)
        admin_bank_details.account_balance = a
        admin_bank_details.save()

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url='http://127.0.0.1:8000/api/bill/',
            cancel_url='http://127.0.0.1:8000/api/charge/'
        )
        return redirect(session.url)
    return redirect("bill")

class BillDetails(APIView):
    def get(self,request):
        return render(request,"bill.html")

class SellerBankDetailsView(APIView):
    def post(self,request):
        if request.user.is_anonymous or not hasattr(request.user, 'role'):
            return Response("Authentication credentials not provided or invalid.", status=400)
        
        if request.user.role=="seller":
            serializer=UserBankDetailsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response("SuccessFully Added Bank Details..")
            else:
                return Response(serializer.errors)
        else:
            return Response("Only Seller can add the details")

    def get(self,request):
        if request.user.is_anonymous or not hasattr(request.user, 'role'):
            return Response("Authentication credentials not provided or invalid.", status=400)
        if request.user.role=="seller":
            details=UserBankDetails.objects.all()
            serializer=UserBankDetailsSerializer(instance=details,many=True)
            return Response(serializer.data)
        else:
            return Response("Only seller user can show details")
        
    def put(self,request,id):
        if request.user.is_anonymous or not hasattr(request.user, 'role'):
            return Response("Authentication credentials not provided or invalid.", status=400)
        
        if request.user.role=="seller":
            product=UpdateUserBankDetailsSerializer.objects.get(id=id)
            serilizer=UpdateUserBankDetailsSerializer(data=request.data,instance=product,partial=True)
            if serilizer.is_valid():
                serilizer.save()
                return Response(serilizer.data)
            else:
                return Response("Invalid Data")
        else:
            return Response("only coomon user can update the Cart")
        
class OrderView(APIView):
    def get(self,request):
        if request.user.is_anonymous or not hasattr(request.user, 'role'):
            return Response("Authentication credentials not provided or invalid.", status=400)
        if request.user.role=="seller":
            details=Order.objects.filter(seller=request.user).all()
            serializer=OrderSerializer(instance=details,many=True)
            return Response(serializer.data)
        else:
            return Response("Only seller user can show details")