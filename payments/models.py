from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import (
    BaseUserManager
)

CHOICES = (
    ("admin", "admin"),
    ("seller", "seller"),
    ("common", "common")
)

class UserManager(BaseUserManager):
    def create_user(self, email,  username, password=None,**extra_fields):

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **extra_fields

        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('acivation_status', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError((
                'Super user must have is_staff'
            ))

        return self.create_user(email,username,password,**extra_fields)

    
class User(AbstractUser):
    phone=models.CharField(max_length=15)
    phone_varified=models.BooleanField(default=False,null=True,blank=True)
    email = models.EmailField(unique=True)
    acivation_status=models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role=models.CharField(max_length=10,choices=CHOICES,null=True,blank=True)
    otp=models.CharField(max_length=10,null=True,blank=True)
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email



class Category(models.Model):
    name=models.CharField(max_length=100)
    type=models.CharField(max_length=10)


    def __str__(self) -> str:
        return self.name

class Product(models.Model):
    name=models.CharField(max_length=100)
    price=models.CharField(max_length=100)
    discription=models.CharField(max_length=150)
    category=models.ForeignKey(Category, on_delete=models.CASCADE)
    seller=models.CharField(max_length=20,blank=True,null=True)


    def __str__(self) -> str:
        return self.name


class Cart(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    products=models.ManyToManyField(Product,through="CartItem")
    product_quantity=models.CharField(max_length=10,default=1)
    product_seller=models.CharField(max_length=100,null=True,blank=True)
    total_bill=models.CharField(max_length=100,null=True,blank=True)
    
    def Product(self):
        return ",".join([str(b) for b in self.products.all()])

class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="cart_items")
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    product_quantity=models.CharField(max_length=10)
    product_seller=models.CharField(max_length=100)
    total_bill=models.CharField(max_length=100)

class DeliveryDetails(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    address1=models.CharField(max_length=50)
    address2=models.CharField(max_length=50)
    city=models.CharField(max_length=50)
    state=models.CharField(max_length=25)
    postal_code=models.CharField(max_length=10)
    country=models.CharField(max_length=25)
    phone_no=models.CharField(max_length=15)
    

class Order(models.Model):
    user = models.CharField(max_length=50)
    product = models.CharField(max_length=50)
    seller = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    



class UserBankDetails(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    user_type=models.CharField(max_length=100,null=True,blank=True)
    bank_name=models.CharField(max_length=100)
    account_number=models.CharField(max_length=10,)
    branch=models.CharField(max_length=100)
    ifsc=models.CharField(max_length=8)
    account_balance=models.CharField(max_length=100,default=0,blank=True,null=True)
