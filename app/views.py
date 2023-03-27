from django.shortcuts import render, redirect
from django.views import View
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
import requests
import random
from .cartquantity import cartquantity
from django.http import HttpResponse

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import ExtractMonth, ExtractDay
from django.db.models import Count
import calendar
from datetime import datetime, time, timedelta

#for genereting pdf invoice
from io import BytesIO
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import xlsxwriter
import os 


def handle_not_found(request, exception):
    return render(request, 'app/page_not_found.html', status=404)
    


def home(request):
    try:
        if 'search' in request.GET:
            search = request.GET['search']
            if search == '':  # handle empty search
                return redirect('home')
            else:
                prod = Product.objects.filter(title__icontains=search)
                if not prod.exists():
                    return redirect('home')
                else:
                    return render(request, 'app/search.html', {'prod': prod})
        else:
            q = None
            if 'user_name' in request.session:
                user = Uuser.objects.get(uname=request.session['user_name'])
                q=cartquantity(user)
            cat_mob = Category.objects.get(name="mobile")
            mobile = Product.objects.filter(category=cat_mob)
            cat_lap = Category.objects.get(name="lap")
            lap = Product.objects.filter(category=cat_lap)
            return render(request, 'app/home.html', {'mob': mobile, 'lap': lap,'quantity':q})
    except Exception as e:
        # handle the exception as per your requirements
        return HttpResponse('Something went wrong: ' + str(e))


def otp(request, phone):
    otp = random.randint(1001, 9999)
    print(otp)
    request.session['otp'] = otp
    url = 'https://www.fast2sms.com/dev/bulkV2'
    message = otp
    numbers = phone
    payload = f'sender_id=TXTIND&message={message}&route=v3&language=english&numbers={numbers}'
    headers = {
    'authorization': "xoiObB7WLa4GvY0uPZ6J9KmS1kXQCA2MeRhpzfTHN5sy8dctVDo5mkyeX9CRJxBKzu8M7FZ0stfh2gdi",
    'Content-Type': "application/x-www-form-urlencoded"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)
    return True

def forgot_password(request):
    if request.method == "GET":
        return render(request, 'app/forgot_password.html')
    else:
        phone = request.POST.get('phone')
        try:
            user = Uuser.objects.get(uphone=phone)
        except Uuser.DoesNotExist:
            user = None

        if user == None:
            messages.warning(request, 'This phone number is not registered')
            return render(request, 'app/forgot_password.html')
        
        
        request.session['phone'] = phone
        otp(request, phone)
        messages.success(request, 'Thank you for giving registered number')
        return redirect('otp_page')

def otp_page(request):
    error_msg = None
    if request.method == 'POST':
        user_otp = int(request.POST.get('user_otp'))
        if request.session.get('otp') == user_otp:
            del request.session['otp']
            phone = int(request.session.get('phone'))
            del request.session['phone']
            user = Uuser.objects.get(uphone=phone)
            request.session['user_id'] = user.id
            request.session['user_name'] = user.uname
            messages.success(request, 'Welcome ' + request.session['user_name'])
            return redirect('home')
        else:
            error_msg = 'invalid otp !'
            return render(request, 'app/otp_page.html', {'error': error_msg})
    else:
        return render(request, 'app/otp_page.html')



class UserRegistrationView(View):
    def get(self, request):
        return render(request, 'app/user_register.html')

    def post(self, request):
        PostData = request.POST
        name = PostData.get('name')
        phone = PostData.get('phone')
        email = PostData.get('email')
        password = PostData.get('password')
        conform_password = PostData.get('conform_password')

        value = {
            'name': name, 'phone': phone, 'email': email
        }

        # save
        error_msg = None
        if (not name) and len(name) < 4:
            error_msg = "name required or should be min 4char's long !"
        elif not name.isalpha():   
            error_msg = "name must contain only letters!" 
        elif (not phone) and len(phone) < 4:
            error_msg = "phone number required or should be 10 digit !"
        elif len(email) < 6:
            error_msg = "Email should be min 8char's long !"
        elif (not password) and len(password) < 6:
            error_msg = "password missing or should be 6char's long.!"
        elif not password == conform_password:
            error_msg = "passwords are not same...!"

        if not error_msg:
            password = make_password(password)
            usr = Uuser(uname=name, uphone=phone, uemail=email, upassword=password)
            usr.save()
            messages.success(request, 'registered succesfully')
            return redirect('user_login')
        else:
            data = {
                'error': error_msg,
                'values': value
            }
            messages.warning(request, 'please provide valid details')
            return render(request, 'app/user_register.html', data)


class user_login(View):
    def get(self, request):
        if 'user_id' in request.session:
            return redirect('home')
        else:
            return render(request, 'app/user_login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email == '':
            messages.warning(request, 'no email found')
            return redirect('user_login')
        if password == '':
            messages.warning(request, 'no password found')
            return redirect('user_login')
        user = Uuser.objects.filter(uemail=email)
        if not user:
                error_msg = 'invalid Email!'
                return render(request, 'app/user_login.html', {'error': error_msg})
        else:
            user = Uuser.objects.get(uemail=email)
            if user is None:
                error_msg = 'invalid Email or password..!'
            
            error_msg = None
            if user:
                flag = check_password(password, user.upassword)
                if flag:
                    if user.uactive:
                        print(user.uactive)
                        request.session['user_id'] = user.id
                        request.session['user_name'] = user.uname
                        messages.success(request, 'Welcome ' + request.session['user_name'])
                        return redirect('home')
                    else:
                        error_msg = 'user is bloked by admin!'
                else:
                    error_msg = 'invalid password..!'
            else:
                error_msg = 'invalid Email or password..!'
        messages.warning(request, 'error in login credentials')
        return render(request, 'app/user_login.html', {'error': error_msg})



class AddressView(View):
    def get(self, request):
        user = Uuser.objects.get(uname=request.session['user_name'])
        q=cartquantity(user)
        form = CustomerAddressForm()
        return render(request, 'app/add_address.html', {'form': form, 'active': 'btn-primary','quantity':q})

    def post(self, request):
        form = CustomerAddressForm(request.POST)
        if form.is_valid():
            user = request.session['user_name']
            user = Uuser.objects.get(uname=user)
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            housename = form.cleaned_data['housename']
            state = form.cleaned_data['state']
            phone = form.cleaned_data['phone']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=user, name=name, locality=locality, housename=housename, city=city, state=state,
                           phone=phone, zipcode=zipcode)
            reg.save()
            messages.success(request, "succesfully added")
            return redirect('address')
        return render(request, 'app/add_address.html', {'form': form, 'active': 'btn-primary'})


def checkout_add_address(request):
    if request.method == 'GET':
        form = CustomerAddressForm()
        messages.warning(request, "please fill")
        return render(request, 'app/add_address.html', {'form': form, 'active': 'btn-primary'})
    if request.method == 'POST':
        form = CustomerAddressForm(request.POST)
        if form.is_valid():
            user = request.session['user_name']
            user = Uuser.objects.get(uname=user)
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            housename = form.cleaned_data['housename']
            state = form.cleaned_data['state']
            phone = form.cleaned_data['phone']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=user, name=name, locality=locality, housename=housename, city=city, state=state,
                           phone=phone, zipcode=zipcode)
            reg.save()
            messages.success(request, "succesfully added")
            return redirect('checkout')
        return render(request, 'app/add_address.html', {'form': form, 'active': 'btn-primary'})


def address(request):
    if "user_name" in request.session:
        user = request.session['user_name']
        user = Uuser.objects.get(uname=user)
        add = Customer.objects.filter(user=user)
        return render(request, 'app/address.html', {'active': 'btn-primary', 'add': add})
    else:
        return redirect('user_login')


def profile(request):
    if "user_name" in request.session:
        user = request.session['user_name']
        add = Uuser.objects.get(uname=user)
        # add = Uuser.objects.filter(uname=user)
        return render(request, 'app/profile.html', {'add': add})
    else:
        return redirect('user_login')


def edit_profile(request):
    user_id = request.GET['add_id']
    user = Uuser.objects.get(id=user_id)
    if request.method == 'POST':
        fm = Profile_form(request.POST, instance=user)
        if fm.is_valid():
            uname = fm.cleaned_data['uname']
            fm.save()
            request.session['user_name'] = uname
            return redirect('profile')
        else:
            return render(request, 'app/edit_profile.html', {'fm': fm})
    else:
        fm = Profile_form(instance=user)
        return render(request, 'app/edit_profile.html', {'fm': fm})

def edit_address(request):
    add_id = request.GET['add_id']
    add = Customer.objects.get(id=add_id)
    if request.method == 'POST':
        fm = CustomerAddressForm(request.POST, instance=add)
        if fm.is_valid():
            fm.save()
            return redirect('address')
        else:
            return render(request, 'app/edit_address.html', {'fm': fm})
    else:
        fm = CustomerAddressForm(instance=add)
        return render(request, 'app/edit_address.html', {'fm': fm})



def delete_address(request):
    if request.method == 'GET':
        address_id = request.GET.get('address_id')
        address = Customer.objects.get(id=address_id)
        address.delete()
        response_data = {'message': 'Address deleted successfully'}
        messages.success(request, 'deleted succesfully')
        return JsonResponse(response_data)


def mobile(request, data=None):
    try:
        if 'search' in request.GET:
            search = request.GET['search']
            if search == '':  # handle empty search
                return redirect('mobile')
            else:
                mob =Product.objects.filter(brand__brand_name__icontains=search)
                if not mob.exists():
                    return redirect('mobile')
                else:
                    return render(request, 'app/mobile.html', {'mob': mob})
    except Exception as e:
            # Handle unexpected errors here
            return HttpResponse('An error occurred: {}'.format(str(e)))

    else:
        cat_mob = Category.objects.get(name="mobile")
        if data == None:
            mob = Product.objects.filter(category=cat_mob)
        elif data == 'Redmi' or data == 'Vivo':
            try:
                data = Brand.objects.get(brand_name=data)
                mob = Product.objects.filter(category=cat_mob, brand=data) 
            except ObjectDoesNotExist:
               mob = Product.objects.filter(category=cat_mob)
        elif data == 'below':
            try:
                mob = Product.objects.filter(category=cat_mob).filter(our_price__lt=10000)
            except ObjectDoesNotExist:
               mob = Product.objects.filter(category=cat_mob)
        elif data == 'above':
            try:
                mob = Product.objects.filter(category=cat_mob).filter(our_price__gt=10000)
            except ObjectDoesNotExist:
               mob = Product.objects.filter(category=cat_mob)
        return render(request, 'app/mobile.html', {'mob': mob})


def lap(request, data=None):
    if 'search' in request.GET:
        search = request.GET['search']
        if search == '':  # handle empty search
            return redirect('lap')
        else:
            lap = Product.objects.filter(brand__brand_name__icontains=search)
            if not lap.exists():
                return redirect('lap')
            else:
                return render(request, 'app/lap.html', {'lap': lap})
    else:
        cat_lap = Category.objects.get(name="lap")
        if data == None:
            lap = Product.objects.filter(category=cat_lap)
        elif data == 'hp' or data == 'Dell':
            try:
                data = Brand.objects.get(brand_name=data)
                lap = Product.objects.filter(category=cat_lap).filter(brand=data)
            except ObjectDoesNotExist:
               lap = Product.objects.filter(category=cat_lap)
        elif data == 'below':
            try:
                lap = Product.objects.filter(category=cat_lap).filter(our_price__lt=30000)
            except ObjectDoesNotExist:
               lap = Product.objects.filter(category=cat_lap)
        elif data == 'above':
            try:
                lap = Product.objects.filter(category=cat_lap).filter(our_price__gt=30000)
            except ObjectDoesNotExist:
               lap = Product.objects.filter(category=cat_lap)
        return render(request, 'app/lap.html', {'lap': lap})


class ProductDetailView(View):
    def get(self, request):
        q = None
        prod_id = request.GET['prod_id']
        prod = Product.objects.get(id=prod_id)
        images = MultipleImage.objects.filter(product=prod)
        color = ColorCombination.objects.filter(product=prod)
        # check the product in cart if in cart show 'already in cart'
        product_found = False
        if 'user_id' in request.session:
            user = request.session['user_name']
            user = Uuser.objects.get(uname=user)
            q=cartquantity(user)
            product_found = Cart.objects.filter(Q(Product=prod_id) & Q(user=user)).exists()
        return render(request, 'app/productdetail.html',
                      {'prod': prod, 'images': images, 'color': color, 'product_found': product_found,'quantity':q})


def logout_page(request):
    try:
        request.session.clear()
    except KeyError:
        messages.warning(request, 'error when logout')
        return redirect("home")
    messages.success(request, 'succesfully logedout')
    return redirect("user_login")


def buy_now(request):
    if 'user_id' in request.session:
        if 'prod_id' in request.session:
            prod_id = request.session['prod_id']
            del request.session['prod_id']
            q = None
            prod = Product.objects.get(id=prod_id)
            images = MultipleImage.objects.filter(product=prod)
            color = ColorCombination.objects.filter(product=prod)
            # check the product in cart if in cart show 'already in cart'
            product_found = False
            if 'user_id' in request.session:
                user = request.session['user_name']
                user = Uuser.objects.get(uname=user)
                q=cartquantity(user)
                product_found = Cart.objects.filter(Q(Product=prod_id) & Q(user=user)).exists()
            return render(request, 'app/productdetail.html',
                      {'prod': prod, 'images': images, 'color': color, 'product_found': product_found,'quantity':q})

        else:
            prod_id = request.GET['prod_id']  
            prod = Product.objects.get(id=prod_id)
            user = request.session['user_name']
            user = Uuser.objects.get(uname=user)
            add = Customer.objects.filter(user=user)
            total_amount = 0.0
            shipping_amount = 70.0
            total_amount = prod.our_price + shipping_amount

            return render(request, 'app/buynow.html', {'prod': prod, 'totalamount': total_amount, 'add': add})
    else:
        return redirect('user_login')
    
def buynow_add_address(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        request.session['prod_id'] = prod_id
        form = CustomerAddressForm()
        messages.warning(request, "please fill")
        return render(request, 'app/add_address.html', {'form': form, 'active': 'btn-primary'})
    if request.method == 'POST':
        form = CustomerAddressForm(request.POST)
        if form.is_valid():
            user = request.session['user_name']
            user = Uuser.objects.get(uname=user)
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            housename = form.cleaned_data['housename']
            state = form.cleaned_data['state']
            phone = form.cleaned_data['phone']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=user, name=name, locality=locality, housename=housename, city=city, state=state,
                           phone=phone, zipcode=zipcode)
            reg.save()
            messages.success(request, "succesfully added new address")
            return redirect('buy_now')
        return render(request, 'app/add_address.html', {'form': form, 'active': 'btn-primary'})

def add_to_cart(request):
    if 'user_id' in request.session:
        user = request.session['user_name']
        user = Uuser.objects.get(uname=user)
        button = request.POST.get('button')
        prod_id = request.POST.get('prod_id')
        prod = Product.objects.get(id=prod_id)
        color = request.POST.get('color')
        color = Color.objects.filter(color=color).first()
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        q = cartquantity(user)
        product_found = False
        if button == 'add_to_cart':
            if cart_product:
                for p in cart_product:
                    if str(p.Product) == prod_id:
                        product_found = True
                        messages.warning(request, 'Already in cart')
            if not product_found:
                Cart(user=user, Product=prod, color= color).save()
                messages.success(request, 'succesfully added')
            return redirect('cart')
        
        if button == 'buy_now':     
            add = Customer.objects.filter(user=user)
            total_amount = 0.0
            shipping_amount = 70.0
            total_amount = prod.our_price + shipping_amount
            return render(request, 'app/buynow.html', {'prod': prod, 'totalamount': total_amount, 'color':color, 'add': add, 'quantity':q})
            
    else:
        return redirect('user_login')


def show_cart(request):
    if "user_name" in request.session:                  
        user = request.session['user_name']
        user = Uuser.objects.get(uname=user)
        coupon_id = request.session.get('coupon_id')
        q = cartquantity(user)
        cart = Cart.objects.filter(user=user)
        discount = 0
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]

        if cart_product:
            for p in cart_product:
                tempamt = (p.quantity * p.Product.our_price)
                amount += tempamt

            if coupon_id:
                try: 
                    coupon = Coupon.objects.get(id=coupon_id)
                    messages.success(request, 'Coupon added successfully')
                    discount = coupon.discount
                    amount = amount - discount
                    total_amount = amount + shipping_amount
                    request.session['total_amount'] = total_amount
                    messages.success(request, 'Discount applied')
                except Coupon.DoesNotExist:
                    messages.warning(request, 'Invalid coupon')
            else:
                total_amount = amount + shipping_amount

            return render(request, 'app/cart.html', {'carts': cart, 'totalamount': total_amount, 'discount':discount, 'amount': amount, 'quantity': q})
        else:
            return render(request, 'app/emptycart.html', {'quantity': q})
    else:
        return redirect('user_login')



def plus_cart(request):
    if request.method == 'GET':
        user = request.session['user_name']
        user = Uuser.objects.get(uname=user)
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(Product=prod_id) & Q(user=user))
        c.quantity += 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        for p in cart_product:
            tempamt = (p.quantity * p.Product.our_price)
            amount += tempamt
            total_amount = amount + shipping_amount

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': total_amount
        }
        return JsonResponse(data)


def minus_cart(request):
    if request.method == 'GET':
        user = request.session['user_name']
        user = Uuser.objects.get(uname=user)
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(Product=prod_id) & Q(user=user))
        c.quantity -= 1
        c.save()
        if c.quantity == 0:
            c.delete()
            amount = 0.0
            shipping_amount = 70.0
            total_amount = 0.0
            cart_product = [p for p in Cart.objects.all() if p.user == user]
            for p in cart_product:
                tempamt = (p.quantity * p.Product.our_price)
                amount += tempamt
                total_amount = amount + shipping_amount

            data = {
                'quantity': c.quantity,
                'amount': amount,
                'totalamount': total_amount
            }
            return JsonResponse(data)
        else:
            amount = 0.0
            shipping_amount = 70.0
            total_amount = 0.0
            cart_product = [p for p in Cart.objects.all() if p.user == user]
            for p in cart_product:
                tempamt = (p.quantity * p.Product.our_price)
                amount += tempamt
                total_amount = amount + shipping_amount

            data = {
                'quantity': c.quantity,
                'amount': amount,
                'totalamount': total_amount
            }
            return JsonResponse(data)


def remove_cart(request):
    if request.method == 'GET':
        user = request.session['user_name']
        user = Uuser.objects.get(uname=user)
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(Product=prod_id) & Q(user=user))

        c.delete()
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        for p in cart_product:
            tempamt = (p.quantity * p.Product.our_price)
            amount += tempamt
            total_amount = amount + shipping_amount

        data = {

            'amount': amount,
            'totalamount': total_amount
        }
        return JsonResponse(data)


def orders(request):
    if 'user_id' in request.session:
        user = request.session['user_name']
        user = Uuser.objects.get(uname=user)
        q = cartquantity(user)
        op = OrderPlaced.objects.filter(user=user).order_by('-ordered_date')
        if op:
            return render(request, 'app/orders.html', {'op': op, 'quantity':q})
        else:
            messages.warning(request, 'No orders found')
            return redirect('home')
    else:
        return redirect('user_login')


def checkout(request):
    if 'user_id' in request.session:
        user = request.session['user_name']
        user = Uuser.objects.get(uname=user)
        add = Customer.objects.filter(user=user)
        coupon_id = request.session.get('coupon_id')
        cart_items = Cart.objects.filter(user=user)
        discount = 0
        q = cartquantity(user)
        if cart_items:
            amount = 0.0
            shipping_amount = 70.0
            total_amount = 0.0
            cart_product = [p for p in Cart.objects.all() if p.user == user]
            if cart_product:
                for p in cart_product:
                    tempamt = (p.quantity * p.Product.our_price)
                    amount += tempamt
                if 'total_amount' in request.session:
                    total_amount = request.session['total_amount'] 
                    del request.session['total_amount']
                else:
                    coupon = Coupon.objects.get(id=coupon_id)
                    discount = coupon.discount
                    amount = amount - discount
                    total_amount = amount + shipping_amount     
                if coupon_id:
                         coupon = Coupon.objects.get(id=coupon_id)
                         discount = coupon.discount
            return render(request, 'app/checkout.html',
                          {'add': add, 'totalamount': total_amount, 'discount':discount, 'cart_items': cart_items, 'quantity':q})
        else:
            return redirect('checkout')
    else:
        return redirect('user_login')
  
def apply_coupon(request):
    if request.method == "POST":
        try:
            coupon_code = request.POST.get('coupon_code')
            coupon = Coupon.objects.filter(code__iexact=coupon_code, active=True)
        except Coupon.DoesNotExist:
            return HttpResponse("Coupon does not exist.")
        if coupon.exists():
            coupon = coupon.first()
            active_date = coupon.active_date
            expiry_date = coupon.expiry_date
            current_date = datetime.now().date()
            if current_date > expiry_date:
                messages.warning(request, 'coupon expired')
                return redirect(show_cart)
            if current_date < active_date:
                messages.warning(request, 'coupon is yet to be available')
                return redirect(show_cart)
            request.session['coupon_id'] = coupon.id
            return redirect(show_cart)
        else:
            messages.warning(request, 'invalid coupon')
            return redirect(show_cart)
  
def payment_done(request):
    
    user = request.session['user_name']
    user = Uuser.objects.get(uname=user)
    custid = request.GET.get('custid')
    totalamount = request.GET.get('totalamount')
    discount = request.GET.get('discount')
    payment_method = request.GET.get('payment_method')
    if payment_method == 'cash on delivery':
        payment_method = 'COD'
    else:
        payment_method = 'pay pal'
    if custid:
        if 'coupon_id' in request.session:
            del request.session['coupon_id']
        customer = Customer.objects.get(id=custid)
        cart = Cart.objects.filter(user=user)
        id = random.randint(1001, 9999)
        for c in cart:
            OrderPlaced(user=user, customer=customer,order_id=id, discount=discount, Product=c.Product, payment_method=payment_method, total_price=totalamount, quantity=c.quantity, color=c.color).save()
            c.delete()
        messages.success(request, 'ordered succesfully')
        return redirect("orders")
    else:
        messages.warning(request, 'No address found')
        return redirect("checkout")
    
    
def buynowpayment_done(request):
    user = request.session['user_name']
    user = Uuser.objects.get(uname=user)
    custid = request.GET.get('custid')
    prod_id = request.GET.get('prod_id')
    color = request.GET.get('color')
    totalamount = request.GET.get('totalamount')
    payment_method = request.GET.get('payment_method')
    if payment_method == 'cash on delivery':
        payment_method = 'cash on delivery'
    else:
        payment_method = 'pay pal'     
    if custid:
        customer = Customer.objects.get(id=custid)
        prod = Product.objects.get(id=prod_id)
        color = Color.objects.filter(color=color).first()
        id = random.randint(1001, 9999)
        OrderPlaced(user=user, customer=customer,order_id=id, Product=prod, payment_method=payment_method, total_price=totalamount, color=color).save()
        messages.success(request, 'ordered succesfully')
        return redirect("orders")
    else:
        request.session['prod_id'] = prod_id
        messages.warning(request, 'No address found')
        return redirect("buy_now")

def cancel_product(request):
    ord_id = request.GET['ord_id']
    ordered_product = OrderPlaced.objects.get(id=ord_id)
    ordered_product.status = 'Cancelled'
    ordered_product.save()
    messages.success(request, 'Order cancelled successfully')
    return redirect('orders')


def invoice(request):
    user = request.session['user_name']
    user = Uuser.objects.get(uname=user)
    ord_id = request.GET['ord_id']
    request.session['ord_id'] = ord_id
    ordered_product = OrderPlaced.objects.get(Q(id=ord_id) & Q(user=user))
    data = {
        'date' : datetime.now().date(),
        'orderid': ordered_product.order_id,
        'ordereddate': ordered_product.ordered_date,
        'name': ordered_product.customer.name,
        'housename': ordered_product.customer.housename,
        'locality' : ordered_product.customer.locality,
        'city' : ordered_product.customer.city, 
        'state' : ordered_product.customer.state, 
        'zipcode': ordered_product.customer.zipcode,
        'phone' : ordered_product.customer.phone,
        'Product': ordered_product.Product.title,
        'Rprice' : ordered_product.Product.real_price,
        'Price' : ordered_product.Product.our_price,
        'quantity': ordered_product.quantity,
        'colour' : ordered_product.color,
        'payment' : ordered_product.payment_method,
        'Shippingcharge': 70, 
        'amount': ordered_product.quantity * ordered_product.Product.our_price,
        'total_cost': ordered_product.total_price,
        'status': ordered_product.status ,
        'saved' : ordered_product.Product.real_price - ordered_product.Product.our_price 
    }
    messages.success(request, 'click download button')
    return render(request, 'app/invoice.html',data)

def download(request):
    user = Uuser.objects.get(uname = request.session['user_name'])
    ordered_product = OrderPlaced.objects.get(Q(id=request.session.get('ord_id')) & Q(user=user))  
    data = {
        'date' : datetime.now().date(),
        'orderid': ordered_product.order_id,
        'ordereddate': ordered_product.ordered_date,
        'name': ordered_product.customer.name,
        'housename': ordered_product.customer.housename,
        'locality' : ordered_product.customer.locality,
        'city' : ordered_product.customer.city, 
        'state' : ordered_product.customer.state, 
        'zipcode': ordered_product.customer.zipcode,
        'phone' : ordered_product.customer.phone,
        'Product': ordered_product.Product.title,
        'Rprice' : ordered_product.Product.real_price,
        'Price' : ordered_product.Product.our_price,
        'quantity': ordered_product.quantity,
        'colour' : ordered_product.color,
        'payment' : ordered_product.payment_method,
        'Shippingcharge': 70, 
        'amount': ordered_product.quantity * ordered_product.Product.our_price,
        'total_cost': ordered_product.total_price,
        'status': ordered_product.status ,
        'saved' : ordered_product.Product.real_price - ordered_product.Product.our_price 
    } 
    template_path = 'app/invoicepdf.html'
    context = {'data': data}
    html = render_to_string(template_path, data)
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{data["orderid"]}.pdf"'
  

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response   
       
import xlsxwriter
from io import BytesIO
from django.http import HttpResponse
from django.db.models import Q
from .models import Uuser, OrderPlaced

def download_excel(request):
    user = Uuser.objects.get(uname=request.session['user_name'])
    ordered_product = OrderPlaced.objects.get(Q(id=request.session.get('ord_id')) & Q(user=user))
    data = {
        'Date': datetime.now().date(),
        'Order id': ordered_product.order_id,
        'Ordered date': ordered_product.ordered_date,
        'Name': ordered_product.customer.name,
        'House name': ordered_product.customer.housename,
        'Locality': ordered_product.customer.locality,
        'City': ordered_product.customer.city,
        'State': ordered_product.customer.state,
        'Pincode': ordered_product.customer.zipcode,
        'Phone': ordered_product.customer.phone,
        'Product name': ordered_product.Product.title,
        'Selling Price': ordered_product.Product.our_price,
        'Offer price': ordered_product.Product.real_price,
        'Quantity': ordered_product.quantity,
        'Colour': str(ordered_product.color),
        'Shipping charge': 70,
        'Amount': ordered_product.quantity * ordered_product.Product.our_price,
        'Total cost': ordered_product.price,
        'Status': ordered_product.status,
        'you saved': ordered_product.Product.real_price - ordered_product.Product.our_price
    }

    # Define the file name and sheet name
    file_name = f'Invoice_{ordered_product.order_id}.xlsx'
    sheet_name = 'Invoice'

    # Create the Excel file
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'remove_timezone': True})
    worksheet = workbook.add_worksheet(sheet_name)

    # Define the column widths and formats
    widths = [15, 15, 15, 15, 15, 15, 15, 15, 15, 15]
    bold = workbook.add_format({'bold': True})
    money_format = workbook.add_format({'num_format': '#,##0.00'})
    date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})

    # Write the data to the Excel file
    row = 0
    col = 0
    for key, value in data.items():
        worksheet.write(row, col, key, bold)
        if key == 'Date' or key == 'Ordered date':
            worksheet.write(row, col + 1, value, date_format)
        else:
            worksheet.write(row, col + 1, value)
        if key in ['Selling price', 'Offer price', 'Amount', 'Total cost', 'You saved']:
            worksheet.write(row, col + 1, value, money_format)
        row += 1

    # Set the column widths
    for i, width in enumerate(widths):
        worksheet.set_column(i, i, width)

    # Close the Excel file and send it as a response
    workbook.close()
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return response

    

def return_product(request):
    ord_id = request.GET['ord_id']
    ordered_product = OrderPlaced.objects.get(id=ord_id)
    ordered_product.status = 'Return'
    ordered_product.save()
    messages.success(request, 'you are returning the product')
    return redirect('orders')





        