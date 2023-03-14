from django import forms
import re
from .models import *

from django import forms
from django.core.exceptions import ValidationError

class CustomerAddressForm(forms.ModelForm):
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    zipcode = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Customer
        fields = ["name", "housename", "locality", "phone", "city", "state", "zipcode"]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'housename': forms.TextInput(attrs={'class': 'form-control'}),
            "locality": forms.TextInput(attrs={'class': 'form-control'}),
            "city": forms.TextInput(attrs={'class': 'form-control'}),
            "state": forms.Select(attrs={'class': 'form-control'}),
            
        }
    
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not re.match(r'^\d{10}$', phone):
            raise ValidationError("Phone number must be entered in the format: '9999999999'")
        return phone
    
    def clean_zipcode(self):
        zipcode = self.cleaned_data['zipcode']
        if not re.match(r'^\d{6}(-\d{4})?$', zipcode):
            raise ValidationError("Zip code must be entered in the format: '00000' or '000000-0000'")
        return zipcode



class Product_form(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ['title', 'our_price', 'real_price', 'description', 'Product_image', 'category','brand']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            "category": forms.Select(attrs={'class': 'form-control'}),
            "brand": forms.Select(attrs={'class': 'form-control'}),
            "our_price": forms.TextInput(attrs={'class': 'form-control'}),
            "real_price": forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_our_price(self):
        our_price = self.cleaned_data.get('our_price')
        if our_price and our_price < 0:
            raise ValidationError("Our price must be a positive number.")
        return our_price

    def clean_real_price(self):
        real_price = self.cleaned_data.get('real_price')
        if real_price and real_price < 0:
            raise ValidationError("Real price must be a positive number.")
        return real_price


class ProductImage_form(forms.ModelForm):
    images = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control', 'multiple': True}))
    class Meta:
        model = MultipleImage
        fields = ['images']
        

class Status_form(forms.ModelForm):
    class Meta:
        model = OrderPlaced
        fields = ['status']
        widgets = {
            "status": forms.Select(attrs={'class': 'form-control'}),

        }


    
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        
    def clean_name(self):
        name = self.cleaned_data['name']
        if not name.isalpha():
            raise forms.ValidationError("Category name must contain only alphabets.")
        return name
    


class Profile_form(forms.ModelForm):
    class Meta:
        model = Uuser
        fields = ['uname']
        widgets = {
            'uname': forms.TextInput(attrs={'class': 'form-control'}),

        }

from django.utils import timezone

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount', 'active', 'active_date', 'expiry_date']
        widgets = {
            'active_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'})
        }

    def clean_active_date(self):
        active_date = self.cleaned_data['active_date']
        if active_date < timezone.now().date():
            raise forms.ValidationError("Active date must be in the future.")
        return active_date

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data['expiry_date']
        if expiry_date < timezone.now().date():
            raise forms.ValidationError("Expiry date must be in the future.")
        return expiry_date

    def clean_discount(self):
        discount = self.cleaned_data['discount']
        if discount <= 0:
            raise forms.ValidationError("Discount must be greater than zero.")
        return discount
    
class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['color']
        widgets = {
            'color': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_color(self):
        color = self.cleaned_data['color']
        if not color.isalpha():
            raise forms.ValidationError("Color name must contain only letters.")
        elif Color.objects.filter(color__iexact=color).exists():
            raise forms.ValidationError("Color already exists.")
        return color

    
class ColorCombinationForm(forms.ModelForm):
    class Meta:
        model = ColorCombination
        fields = ['color', 'stock', 'product']

    def clean_stock(self):
        stock = self.cleaned_data['stock']
        if stock <= 0:
            raise forms.ValidationError("Stock must be a positive integer")
        return stock
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].label_from_instance = lambda obj: obj.title    


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['brand_name', 'brand_image']
        
        
    def clean_brand_name(self):
        name = self.cleaned_data['brand_name']
        if not name.isalpha():
            raise forms.ValidationError("Brand name must contain only alphabets.")
        return name

    def clean_brand_image(self):
        brand_image = self.cleaned_data['brand_image']
        if not brand_image:
            raise forms.ValidationError('You must select an image.')
        else:
            if brand_image.size > 4*1024*1024:
                raise forms.ValidationError('Image file too large ( > 4mb )')
        return brand_image
    
    
    

          

    