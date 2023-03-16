from django.shortcuts import render, redirect
from django.views import View
from app.models import *
from app.forms import *
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import ExtractMonth
from django.db.models import Count, Sum
import calendar
from datetime import datetime, time
from django.contrib.auth.decorators import user_passes_test
from django.db.models import F, Sum
from django.http import HttpResponse

#for genereting pdf invoice
from io import BytesIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa


def admin_login(request):
    error_msg = None
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    elif request.method == 'GET':
        return render(request, 'app/admin_login.html')
    else:
        if request.method == 'POST':
            name = request.POST.get('name')
            password = request.POST.get('password')

            user = authenticate(request, username=name, password=password)

            if user is not None:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                error_msg = 'invalid Name or password..!'

    return render(request, 'app/admin_login.html', {'error': error_msg})

@user_passes_test(lambda user: user.is_superuser)
def admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    try:
        mobiles_category = Category.objects.get(name='mobile')
    except ObjectDoesNotExist:
    # Handle the case where the object does not exist
        mobiles_category = None

    try:
        laptops_category = Category.objects.get(name='lap')
    except ObjectDoesNotExist:
    # Handle the case where the object does not exist
        laptops_category = None

    mobile_orders_count = OrderPlaced.objects.filter(Product__category=mobiles_category).aggregate(
        Sum('quantity'))['quantity__sum'] or 0
    lap_orders_count = OrderPlaced.objects.filter(Product__category=laptops_category).aggregate(
        Sum('quantity'))['quantity__sum'] or 0
    print('mob', mobile_orders_count)
    print('laps', lap_orders_count)

    orders_months = OrderPlaced.objects.annotate(month=ExtractMonth("ordered_date")).values('month').annotate(
        count=Count('id')).values('month', 'count')

    months = []
    total_ord = []

    for i in orders_months:
        months.append(calendar.month_name[i['month']])
        total_ord.append(int(i['count']))

    orders = OrderPlaced.objects.order_by('-ordered_date')[:2]

    context = {
        'months': months,
        'total_ord': total_ord,
        'mobile_orders_count': mobile_orders_count,
        'lap_orders_count': lap_orders_count,
        'latest_orders': orders,
    }

    return render(request, 'app/admin_dashboard.html', context)


@user_passes_test(lambda user: user.is_superuser)
def admin_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("admin_login")

@user_passes_test(lambda user: user.is_superuser)
def admin_users(request):
    if request.user.is_authenticated:
        try:
            if 'search' in request.GET:
                search = request.GET['search']
                if search == '':  # handle empty search
                    return redirect('admin_users')
                else:
                    user = Uuser.objects.filter(uname__icontains=search)
                    if not user.exists():
                        return redirect('admin_users')
                    else:
                        return render(request, 'app/admin_user.html', {'user': user})

            else:
                user = Uuser.objects.all()
                return render(request, 'app/admin_user.html', {'user': user})
        except Exception as e:
            # Handle the exception here, e.g. log it or show an error message
            print(e)
            return HttpResponse("An error occurred")
    else:
       return redirect('admin_login')
     

@user_passes_test(lambda user: user.is_superuser)
def userblock(request):
    if request.user.is_authenticated:
        try:
            cust_id = request.GET['cust_id']
        except KeyError:
            # Handle the case where 'cust_id' is not present in the GET request
            return HttpResponse("Missing 'cust_id' parameter")
        check = Uuser.objects.filter(id=cust_id)
        for x in check:
            if x.uactive:
                Uuser.objects.filter(id=cust_id).update(uactive=False)
            else:
                Uuser.objects.filter(id=cust_id).update(uactive=True)
        return redirect(admin_users)
    else:
        return redirect('admin_login')
# ----------------admin products-------------------

@user_passes_test(lambda user: user.is_superuser)
def admin_products(request):
    if request.user.is_authenticated:
        try:
            if 'search' in request.GET:
                search = request.GET['search']
                if search == '':  # handle empty search
                    return redirect('admin_products')
                else:
                    prod = Product.objects.filter(title__icontains=search)
                    if not prod.exists():
                        return redirect('admin_products')
                    else:
                        return render(request, 'app/admin_products.html', {'products': prod})
            else:
                products = Product.objects.all()
                return render(request, 'app/admin_products.html', {'products': products})
        except Exception as e:
            # log the error or handle it in some other way
            return HttpResponse('Something went wrong!')
    else:
        return redirect('admin_login')

@user_passes_test(lambda user: user.is_superuser)
def add_new_product(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            files = request.FILES.getlist('images')
            fm = Product_form(request.POST, request.FILES)
            form = ProductImage_form(request.POST, request.FILES)
            if fm.is_valid() and form.is_valid():
                prod = fm.save()
                messages.success(request, "added new product")
                for file in files:
                    MultipleImage.objects.create(product=prod, images=file)
                return redirect('admin_products')
            else:
                return render(request, 'app/add_new_product.html', {'fm': fm, 'form': form})
        else:
            fm = Product_form()
            form = ProductImage_form()
            return render(request, 'app/add_new_product.html', {'fm': fm, 'form': form})
    else:
        return redirect('admin_login')    


from django.forms import inlineformset_factory


@user_passes_test(lambda user: user.is_superuser)
def edit_product(request, id):
    if request.user.is_authenticated:
        try:
            prod = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return HttpResponse("Product does not exist")

        ImageFormSet = inlineformset_factory(Product, MultipleImage, fields=('images',), extra=3)

        if request.method == 'POST':
            fm = Product_form(request.POST, request.FILES, instance=prod)
            formset = ImageFormSet(request.POST, request.FILES, instance=prod)
            if fm.is_valid() and formset.is_valid():
                fm.save()
                formset.save()
                return redirect('admin_products')
            else:
                return render(request, 'app/edit_product.html', {'fm': fm, 'formset': formset})
        else:
            fm = Product_form(instance=prod)
            formset = ImageFormSet(instance=prod)
        return render(request, 'app/edit_product.html', {'fm': fm, 'formset': formset})
    else:
        return redirect('admin_login')


@user_passes_test(lambda user: user.is_superuser)
def delete_product(request, id):
    if request.user.is_authenticated:
        try:
            prod = Product.objects.get(id=id)
            prod.delete()
            return redirect('admin_products')
        except Product.DoesNotExist:
            # Handle the case where the product does not exist
            # For example, you could redirect to an error page
             return HttpResponse("Product does not exist")
    else:
        return redirect('admin_login')


@user_passes_test(lambda user: user.is_superuser)
def admin_orders(request):
    if request.user.is_authenticated:
        try:
            if 'search' in request.GET:
                search = request.GET['search']
                if search == '':  # handle empty search
                    return redirect('admin_orders')
                else:
                    prod = OrderPlaced.objects.filter(Product__title__icontains=search) or OrderPlaced.objects.filter(order_id__icontains=search)
                    if not prod.exists():
                        return redirect('admin_orders')
                    else:
                        return render(request, 'app/admin_orders.html', {'product': prod})
            else:
                product = OrderPlaced.objects.all().order_by('-ordered_date')
                return render(request, 'app/admin_orders.html', {'product': product})
        except Exception as e:
            # Handle any exceptions that might occur here
            return HttpResponse(f"An error occurred: {e}")
    else:
        return redirect("admin_login")



@user_passes_test(lambda user: user.is_superuser)
def edit_status(request):
    if request.user.is_authenticated:
        prod_id = request.GET.get('prod_id')
        try:
            prod = OrderPlaced.objects.get(id=prod_id)
        except OrderPlaced.DoesNotExist:
            return HttpResponse('Invalid product id')
        
        if request.method == 'POST':
            fm = Status_form(request.POST, instance=prod)
            if fm.is_valid():
                fm.save()
                return redirect('admin_orders')
            else:
                return render(request, 'app/edit_status.html', {'fm': fm})
        else:
            fm = Status_form(instance=prod)
            return render(request, 'app/edit_status.html', {'fm': fm})
    else:
        return redirect('admin_login')


# ----------------admin category-------------------

@user_passes_test(lambda user: user.is_superuser)
def admin_category(request):
    if request.user.is_authenticated:
        try:
            if request.method == "GET":
                category = Category.objects.all()
                return render(request, 'app/admin_category.html', {'category': category})
        except Exception as e:
            # handle the exception here
           return HttpResponse('error')
    else:
        return redirect('admin_login')
  

@user_passes_test(lambda user: user.is_superuser)
def add_new_category(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            fm = CategoryForm(request.POST)
            if fm.is_valid():
                fm.save()
                return redirect('admin_category')
            else:
                return render(request, 'app/add_new_category.html', {'fm': fm})
        else:
            fm = CategoryForm()
            return render(request, 'app/add_new_category.html', {'fm': fm})
    else:
        return redirect('admin_login') 

@user_passes_test(lambda user: user.is_superuser)
def edit_category(request, id):
    if request.user.is_authenticated:
        try:
            cat = Category.objects.get(id=id)
        except Category.DoesNotExist:
            return HttpResponse('Category not found')
            
        if request.method == 'POST':
            fm = CategoryForm(request.POST, instance=cat)
            if fm.is_valid():
                fm.save()
                return redirect('admin_category')
            else:
                return render(request, 'app/edit_category.html', {'fm': fm})
        else:
            fm = CategoryForm(instance=cat)
            return render(request, 'app/edit_category.html', {'fm': fm})
    else:
        return redirect('admin_login')
 

@user_passes_test(lambda user: user.is_superuser)
def delete_category(request, id):
    if request.user.is_authenticated:
        try:
            cat = Category.objects.get(id=id)
            cat.delete()
        except Category.DoesNotExist:
            # handle the case when the category with the given id does not exist
            return HttpResponse('Category not found')
        
        return redirect('admin_category')
    else:
        return redirect('admin_login')


# ----------------admin brand-------------------

@user_passes_test(lambda user: user.is_superuser)
def admin_brand(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            try:
                search = request.GET['search']
                if search == '':  # handle empty search
                    return redirect('admin_brand')
                else:
                    brand = Brand.objects.filter(brand_name__icontains=search)
                    if not brand.exists():
                        return redirect('admin_brand')
                    else:
                        return render(request, 'app/admin_brand.html', {'brand': brand})
            except KeyError:
                brand = Brand.objects.all()
                return render(request, 'app/admin_brand.html', {'brand': brand})
    else:
        return redirect('admin_login')
     


@user_passes_test(lambda user: user.is_superuser)
def add_new_brand(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            fm = BrandForm(request.POST, request.FILES)
            if fm.is_valid():
                fm.save()
                return redirect('admin_brand')
            else:
                return render(request, 'app/add_new_brand.html', {'fm': fm})
        else:
            fm = BrandForm()
            return render(request, 'app/add_new_brand.html', {'fm': fm})
    else:
        return redirect('admin_login')     


@user_passes_test(lambda user: user.is_superuser)
def edit_brand(request, id):
    if request.user.is_authenticated:
        try:
            brand = Brand.objects.get(id=id)
        except Brand.DoesNotExist:
            # handle the exception
            return HttpResponse("Brand not found", status=404)
        
        if request.method == 'POST':
            fm = BrandForm(request.POST, request.FILES, instance=brand)
            if fm.is_valid():
                fm.save()
                return redirect('admin_brand')
            else:
                return render(request, 'app/edit_brand.html', {'fm': fm})
        else:
            fm = BrandForm(instance=brand)
            return render(request, 'app/edit_brand.html', {'fm': fm})
    else:
        return redirect('admin_login')
  


@user_passes_test(lambda user: user.is_superuser)
def delete_brand(request, id):
    if request.user.is_authenticated:
        try:
            brand = Brand.objects.get(id=id)
            brand.delete()
            return redirect('admin_brand')
        except Brand.DoesNotExist:
            # Handle the case where the Brand object does not exist
            return HttpResponse('Brand not found')
    else:
        return redirect('admin_login')


# ----------------admin coupon-------------------

@user_passes_test(lambda user: user.is_superuser)
def admin_coupon(request):
    if request.user.is_authenticated:
        try:
            if request.method == "GET":
                coupon = Coupon.objects.all()
                return render(request, 'app/admin_coupon.html', {'coupon': coupon})
        except Exception as e:
            # handle the exception here
            return HttpResponse("An error occurred.")
    else:
        return redirect('admin_login')
   

@user_passes_test(lambda user: user.is_superuser)
def add_new_coupon(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            fm = CouponForm(request.POST)
            if fm.is_valid():
                fm.save()
                return redirect('admin_coupon')
            else:
                return render(request, 'app/add_new_coupon.html', {'fm': fm})
        else:
            fm = CouponForm()
            return render(request, 'app/add_new_coupon.html', {'fm': fm})
    else:
        return redirect('admin_login') 

@user_passes_test(lambda user: user.is_superuser)
def edit_coupon(request, id):
    if request.user.is_authenticated:
        try:
            cat = Coupon.objects.get(id=id)
        except Coupon.DoesNotExist:
            # Handle the exception here, e.g. redirect to a 404 page
            return HttpResponse('Coupon not found')
            
        if request.method == 'POST':
            fm = CouponForm(request.POST, instance=cat)
            if fm.is_valid():
                fm.save()
                return redirect('admin_coupon')
            else:
                return render(request, 'app/edit_coupon.html', {'fm': fm})
        else:
            fm = CouponForm(instance=cat)
            return render(request, 'app/edit_coupon.html', {'fm': fm})
    else:
        return redirect('admin_login')


@user_passes_test(lambda user: user.is_superuser)
def delete_coupon(request, id):
    if request.user.is_authenticated:
        try:
            coupon = Coupon.objects.get(id=id)
            coupon.delete()
        except Coupon.DoesNotExist:
            return HttpResponse("Coupon does not exist.")
        return redirect('admin_coupon')
    else:
        return redirect('admin_login')

        
# ----------------admin colours-------------------

@user_passes_test(lambda user: user.is_superuser)
def admin_colours(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            color = Color.objects.all()
            return render(request, 'app/admin_colour.html', {'color': color})
    else:
        return redirect('admin_login') 

@user_passes_test(lambda user: user.is_superuser)
def add_new_colours(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            fm = ColorForm(request.POST)
            if fm.is_valid():
                fm.save()
                return redirect('admin_colours')
            else:
                return render(request, 'app/add_new_colour.html', {'fm': fm})
        else:
            fm = ColorForm()
        return render(request, 'app/add_new_colour.html', {'fm': fm})
    else:
        return redirect('admin_login') 

@user_passes_test(lambda user: user.is_superuser)
def edit_colours(request, id):
    if request.user.is_authenticated:
        try:
            color = Color.objects.get(id=id)
        except Color.DoesNotExist:
            # handle the case where the color with the given id does not exist
            return HttpResponse('Color not found')
        
        if request.method == 'POST':
            fm = ColorForm(request.POST, instance=color)
            if fm.is_valid():
                fm.save()
                return redirect('admin_colours')
            else:
                return render(request, 'app/edit_colour.html', {'fm': fm})
        else:
            fm = ColorForm(instance=color)
            return render(request, 'app/edit_colour.html', {'fm': fm})
    else:
        return redirect('admin_login')


@user_passes_test(lambda user: user.is_superuser)
def delete_colours(request, id):
    if request.user.is_authenticated:
        try:
            cat = Color.objects.get(id=id)
            cat.delete()
            return redirect('admin_colours')
        except Color.DoesNotExist:
            return HttpResponse("colour not exist.")
    else:
        return redirect('admin_login')



# ----------------admin colour combinations-------------------

@user_passes_test(lambda user: user.is_superuser)
def admin_Colour_combination(request):
    if request.user.is_authenticated:
        try:
            if 'search' in request.GET:
                search = request.GET['search']
                if search == '':  # handle empty search
                    return redirect('admin_Colour_combination')
                else:
                    color = ColorCombination.objects.filter(product__title__icontains=search)
                    if not color.exists():
                        return redirect('admin_Colour_combination')
                    else:
                        return render(request, 'app/admin_colourcombination.html', {'color': color})

            if request.method == "GET":
                color = ColorCombination.objects.order_by('product__title')
                return render(request, 'app/admin_colourcombination.html', {'color': color})
        except Exception as e:
            # Handle unexpected errors here
            return HttpResponse('An error occurred: {}'.format(str(e)))
    else:
        return redirect('admin_login')


@user_passes_test(lambda user: user.is_superuser)
def add_new_colour_combination(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            fm = ColorCombinationForm(request.POST)
            if fm.is_valid():
                fm.save()
                return redirect('admin_Colour_combination')
            else:
                return render(request, 'app/add_colourcombination.html', {'fm': fm})
        else:
            fm = ColorCombinationForm()
            return render(request, 'app/add_colourcombination.html', {'fm': fm})
    else:
        return redirect('admin_login')


@user_passes_test(lambda user: user.is_superuser)
def edit_colour_combination(request, id):
    if request.user.is_authenticated:
        try:
            color = ColorCombination.objects.get(id=id)
        except ColorCombination.DoesNotExist:
            return HttpResponse("Color combination not found")
        
        if request.method == 'POST':
            fm = ColorCombinationForm(request.POST, instance=color)
            if fm.is_valid():
                fm.save()
                return redirect('admin_Colour_combination')
            else:
                return render(request, 'app/edit_colourcombination.html', {'fm': fm})
        else:
            fm = ColorCombinationForm(instance=color)
            return render(request, 'app/edit_colourcombination.html', {'fm': fm})
    else:
        return redirect('admin_login')



@user_passes_test(lambda user: user.is_superuser)
def delete_colour_combination(request, id):
    if request.user.is_authenticated:
        try:
            cat = ColorCombination.objects.get(id=id)
        except ColorCombination.DoesNotExist:
            # Handle the case where the ColorCombination doesn't exist
            return HttpResponse('The ColorCombination you are trying to delete does not exist.')
        else:
            cat.delete()
            return redirect('admin_Colour_combination')
    else:
        return redirect('admin_login')

        

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import requests  
from django.template.loader import get_template       
import openpyxl
import pytz

@user_passes_test(lambda user: user.is_superuser)
def sales_report(request):
    if request.method == 'POST':  
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        generate = request.POST.get('generate')
        order = OrderPlaced.objects.all()
        if end_date < start_date:
            messages.warning(request, 'invalid date')
            return redirect(admin_dashboard)
            
        if generate == 'PDF':
            if start_date and end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                orders = OrderPlaced.objects.filter(ordered_date__range=[start_date, end_date]) 
            if start_date == '' and end_date == '':
                orders = OrderPlaced.objects.all()
            total_orders = OrderPlaced.objects.aggregate(total_orders=Count('id'))['total_orders']
            delivered_orders = OrderPlaced.objects.filter(status=STATUS_CHOICES[4][0])
            total_delivered_products = delivered_orders.aggregate(Sum('quantity'))['quantity__sum'] or 0
            total_price = OrderPlaced.objects.filter(status='Delivered').aggregate(Sum('total_price'))['total_price__sum']
            mobile_orders_count = OrderPlaced.objects.filter(Product__category= Category.objects.get(name='mobile')).aggregate(Sum('quantity'))['quantity__sum']
            lap_orders_count = OrderPlaced.objects.filter(Product__category= Category.objects.get(name='lap')).aggregate(Sum('quantity'))['quantity__sum']
            now=datetime.today()
            data={
                'now': now,
                'orders':orders,
                'total_orders':total_orders,
                'start_date':start_date,
                'end_date':end_date,
                'mobile_orders_count':mobile_orders_count,
                'lap_orders_count':lap_orders_count,
                'total_amount_received':total_price,
                'delivered_orders':total_delivered_products,
            }
            # return render(request,'app/salesreport.html',data) 
            response = HttpResponse(content_type='application/pdf')
            filename = "Report"+str(now)+ ".pdf"
            content = "filename="+filename
            response['Content-Disposition'] = content
            template = get_template("app/salesreport.html")
            html = template.render(data)
            result = BytesIO()
            pdf = pisa.pisaDocument( BytesIO(html.encode("ISO-8859-1")), result)
            if not pdf.err:
                return HttpResponse(result.getvalue(), content_type='application/pdf')
            return response
        
        elif generate == 'Excel': 
            if start_date and end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                default_time = time(hour=0, minute=0, second=0)
                print(start_date)
                print(end_date)
                total_ordered_products = OrderPlaced.objects.filter(ordered_date__range=[start_date, end_date])

            else:
                total_ordered_products = OrderPlaced.objects.all()
                
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(['Order id', 'Email' , 'Status' ,'payment method', 'Product' , 'Amount',])
            for order in total_ordered_products:
                date = order.ordered_date.astimezone(pytz.utc).replace(tzinfo=None)
                ws.append([order.order_id, order.user.uemail, order.status, order.payment_method, order.Product.title,order.Product.our_price,])
            file_name = "sales_report.xlsx"
            wb.save(file_name)
            with open(file_name, "rb") as f:
                response = HttpResponse(f.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                response["Content-Disposition"] = f"attachment; filename={file_name}"
                return response

    else:
        return redirect('admin_dashboard')
