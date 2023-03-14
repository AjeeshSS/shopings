from django.contrib import admin
from .models import *
import admin_thumbnails

@admin_thumbnails.thumbnail('image')




@admin.register(Uuser)
class UuserModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'uname', 'uemail']


@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'locality', 'city', 'zipcode', 'state']


@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'our_price', 'real_price', 'description', 'category']


@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user']


@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'customer', 'quantity', 'ordered_date', 'status']
    
@admin.register(Category)
class CategoryModelAdmin(admin.ModelAdmin):
    list_display = ['name']    
    

admin.site.register(MultipleImage)   
admin.site.register(Coupon)     
# admin.site.register(Color) 
@admin.register(Color)
class ColorModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'color']
    
@admin.register(ColorCombination)
class ColorCombinationModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'color','stock','product']    
    
@admin.register(Brand)
class BrandModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'brand_name','brand_image']    
