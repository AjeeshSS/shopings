from django.db import models


# Create your models here.

class Uuser(models.Model):
    uname = models.CharField(max_length=50)
    uphone = models.BigIntegerField()
    uemail = models.EmailField()
    upassword = models.CharField(max_length=500)
    uactive = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)
    
BRAND_CHOICES = (
    ('acer', 'acer'),
    ('Vivo', 'Vivo'),
    ('mac', 'mac'),
    ('hp', 'hp'),
    ('Dell', 'Dell'),
    ('realme', 'realme'),
    ('Redmi', 'Redmi'),
    ('one plus', 'one plus'),
    ('Samsung', 'Samsung'),
)

class Brand(models.Model):
    brand_name = models.CharField(max_length=50)
    brand_image = models.ImageField(upload_to='productimg')
    def __str__(self):
        return self.brand_name

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

STATE_CHOICES = (
    ('KARNATAKA', 'KARNATAKA'),
    ('KERALA', 'KERALA'),
    ('TAMIL NADU', 'TAMIL NADU'),
    ('GOA', 'GOA'),
    ('GUJARAT', 'GUJARAT')
)


class Customer(models.Model):
    user = models.ForeignKey(Uuser, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=12)
    housename = models.CharField(max_length=50)
    locality = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=50)
    state = models.CharField(choices=STATE_CHOICES, max_length=50)

    def __str__(self):
        return str(self.id)




class Product(models.Model):
    title = models.CharField(max_length=100)
    our_price = models.FloatField()
    real_price = models.FloatField() 
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE,)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    Product_image = models.ImageField(upload_to='productimg')
    
    def __str__(self):
        return str(self.id)
    
class MultipleImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    images = models.ImageField(upload_to='productimg')
    
    def __str__(self):
        return self.product.title


     
class Color(models.Model):
    color = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.color  
    
class ColorCombination(models.Model):
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='color_combinations')
    stock = models.PositiveIntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='color_combinations')

    def __str__(self):
        return self.color 
    # def __str__(self):
    #     return f'{self.color.name} - {self.product.name}' 
    
class Cart(models.Model):
    user = models.ForeignKey(Uuser, on_delete=models.CASCADE, default=1)
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)
    color = models.ForeignKey(Color, on_delete=models.CASCADE,default=1)

    
    def __str__(self):
        return str(self.user)

    @property
    def total_cost(self):
        return self.quantity * self.Product.our_price


STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On the way', 'On the way'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
    ('Return', 'Return'),
)


class OrderPlaced(models.Model):
    user = models.ForeignKey(Uuser, on_delete=models.CASCADE, default=1)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_id = models.PositiveIntegerField(default=1)
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    ordered_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    total_price = models.FloatField()
    discount = models.FloatField(default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')

    # @property
    # def total_cost(self):
    #     return self.quantity * self.Product.our_price + 70


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.FloatField(help_text='Discount in rupees')     
    active = models.BooleanField(default=True)
    active_date = models.DateField()
    expiry_date = models.DateField()
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) ->str:
        return self.code   


