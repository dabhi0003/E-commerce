from django.contrib import admin
from .models import User,Category,Product,Cart,DeliveryDetails,UserBankDetails,CartItem,Order
from django.contrib.admin import ModelAdmin

class UserAdmin(ModelAdmin):
        list_display = ('id', 'email', 'username', 'first_name', 'last_name' ,"otp","phone_varified",'phone','role','acivation_status')
        list_filter = ('is_superuser',)
        fieldsets = [
                (None, {'fields': ('email', 'password',)}),
                ('Personal info', {'fields': ('first_name', 'last_name',"otp"
                ,"phone_varified", 'role','username','phone','acivation_status',)}),
                ('Permissions', {'fields': ('is_superuser',)}),
        ]

        add_fieldsets = (
                (None, {
                        'classes': ('wide',),
                        'fields': ( 'is_student','phone','acivation_status'),
                }),
        )
        search_fields = ('username',)
        ordering = ('id',)
        filter_horizontal = ()
admin.site.register(User, UserAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["type", "name"][::-1]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["seller","category", "discription", "price", "name"][::-1]


@admin.register(Cart)
class UserProductAdmin(admin.ModelAdmin):
    list_display = ["product_seller","total_bill","product_quantity", "get_products","user"][::-1] 

    def get_products(self, obj):
        return ", ".join([str(product) for product in obj.products.all()])

    get_products.short_description = 'products'


@admin.register(DeliveryDetails)
class DeliveryDetailsAdmin(admin.ModelAdmin):
    list_display = ["phone_no", "country", "postal_code", "state", "city", "address2", "address1", "user"][::-1]


@admin.register(UserBankDetails)
class SellerBankDetailsAdmin(admin.ModelAdmin):
    list_display = ["user_type","account_balance","ifsc", "branch", "account_number", "bank_name", "user"][::-1]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["total_bill", "product_seller", "product_quantity", "product", "cart"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [ "quantity", "price", "seller", "product", "user"][::-1]
