from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User, Group
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from google.oauth2 import id_token
from google.auth.transport.requests import Request
from .models import Product, Category, Catalog, Product_catalog, Promotion, Profile, Order, Order_Details, Application, Sponsor
from .forms import AddProductsForm, AccountCreationForm, DriverCreationForm, AdminCreationForm, SponsorCreationForm, LoginForm, PromoCreateForm, ReportsDriverPointsLogForm, UserInfoUpdateForm
from werkzeug.security import check_password_hash
from django.views.generic.edit import FormView
from django.contrib import messages
#from .audit import log_login_attempts, log_account_creation, log_password_change, log_points_added, log_points_removed, download_logs
from .audit import *
from .ebay_api import EbayAPI
from django.conf import settings
from ebaysdk.trading import Connection as Trading
from ebaysdk.shopping import Connection as Shopping
from .report import *
import requests
import csv
import datetime
import os

# View for inital endpoint
class HomepageView(generic.TemplateView):
    template_name = 'gdrp/Homepage.html'
    context_object_name = 'Homepage'

# to change to Sponsor view (unimplemented)
class ToSView(generic.TemplateView):
    template_name = 'gdrp/termsofservice.html'
    context_object_name = 'Terms of Service'

# view for Privacy policy page
class PrivacyPolicyView(generic.TemplateView):
    template_name = 'gdrp/privacypolicy.html'
    context_object_name = 'Privacy Policy' 

# view for the user dashboard 
class DashboardView(generic.TemplateView):
    template_name = 'gdrp/dashboard.html'
    context_object_name = 'Dashboard'

# page to create a sponsor object
class SponsorCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.TemplateView):
    template_name = 'gdrp/create_sponsor.html'
    login_url = 'gdrp:admin_login'
    
    def post(self, request):
        name = request.POST.get('name')
        sponsor = Sponsor.objects.create(name=name)
        sponsor.save()

        return redirect('gdrp:dash_admin')
    
    def test_func(self):
        return self.request.user.groups.filter(name='admin').exists()

class PromotionCreateView(FormView):
    template_name = "gdrp/promotion-Create.html"
    form_class = PromoCreateForm
    #success_url = '.'
    success_url = '.'
    

    # Currently Does not function as intended
    # 

    def form_valid(self, form):
        name = str(form.data.get('name'))
        desc = str(form.data.get('description'))
        mult = float(form.data.get('multiplier'))
        print(name, desc, mult)
        promo = Promotion(name = name, description = desc, multiplier = mult)
        promo.save()
        return super().form_valid(form)

class PromotionListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "gdrp/dash_driver.html"
    login_url = 'gdrp:admin_login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user=self.request.user)
        context['promotion_list'] = profile.promotions.all()
        return context

class AddProductsFormView(generic.FormView):
    template_name = "gdrp/add_multi_products.html"
    form_class = AddProductsForm

    def form_valid(self, form):
        etsy_pids = form.cleaned_data['etsy_pids']
        pid_list = [int(id) for id in etsy_pids.split()]

        cat_id = form.cleaned_data('catalog')
        if (cat_id):
            catalog = Catalog.objects.get(id=cat_id)
        # Use EtsyController to add products to the catalog.

        return super().form_valid(form)

class DriverDashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = "gdrp/dash_driver.html"
    context_object_name = "Driver Dashboard"
    login_url = 'gdrp:driver_login'
    #promotion_list = 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user=self.request.user)
        
        # Eventually fix the promotions table in the DB
        #context['promotion_list'] = profile.promotions.all()
        context['promotion_list'] = Promotion.objects.all()
        if self.request.method == "POST":
            context['message'] = self.request.POST.get('message')
        return context
    

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, generic.TemplateView):
    template_name = "gdrp/dash_admin.html"
    context_object_name = "Admin Dashboard"
    login_url = 'gdrp:admin_login'

    def test_func(self):
        return self.request.user.groups.filter(name='admin').exists()

class SponsorDashboardView(LoginRequiredMixin, UserPassesTestMixin, generic.TemplateView):
    template_name = "gdrp/dash_sponsor.html"
    context_object_name = "Sponsor Dashboard"
    login_url = 'gdrp:sponsor_login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        catalogs = Catalog.objects.all()
        applications =  Application.objects.filter(approved=False)
        context['applications'] = applications
        context['catalogs'] = catalogs
        if self.request.method == "POST":
            context['message'] = self.request.POST.get('message')
            
            # create a new application object and save it
            application = Application.objects.create(driver=self.request.user.driver_profile)
            
            # notify the sponsor of the new application
            messages.add_message(self.request, messages.SUCCESS, 'You have a new application to view!')

        return context

    def test_func(self):
        isAdmin = self.request.user.groups.filter(name='admin').exists()
        isSponsor = self.request.user.groups.filter(name='Sponsors').exists()
        return isAdmin or isSponsor

    
class UserInfo(LoginRequiredMixin, generic.UpdateView):
    model = User
    form_class = UserInfoUpdateForm
    template_name = 'gdrp/account_info.html'
    context_object_name = 'user'
    success_url = reverse_lazy('gdrp:account_info')
    login_url = 'gdrp:admin_login'

    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response =  super().form_valid(form)

        profile = self.object.profile
        profile.phone = int(form.cleaned_data['phone'])
        profile.save()

        return response
    
# view for a specific product 
class ProductView(generic.DetailView):
    model = Product
    template_name = 'gdrp/product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        image = request.FILES.get('image')
        # This updates the image of the product
        # when an admin uploads one.
        if image:
            self.object.image = image
            self.object.save()
        # This updates the stock of the product
        inventory = request.POST.get('inventory')
        if inventory:
            self.object.inventory = int(inventory)
            self.object.save()
            
        category_pk = request.POST.get('category')
        if category_pk:
            category = Category.objects.get(pk=category_pk)
            
            self.object.category = category
            self.object.save()
        return redirect(self.object.get_absolute_url())
        

# view for password reset page
class PasswordReset(generic.TemplateView):
    template_name = "gdrp/password_reset.html"
    context_object_name = "Password Reset"

# view for general user login (unused)
class UserLoginView(generic.TemplateView):
    template_name = "gdrp/user_login.html"
    context_object_name = "User Account Login"

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.user.is_authenticated:
            return redirect('gdrp:dashboard')
        return response

# view for Driver group login
class DriverLoginView(LoginView):
    template_name = "gdrp/Good_Driver.Driver_Login.html"
    context_object_name = "Driver Login"
    form_class = LoginForm

    def form_valid(self, form):
        # user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        username = form.cleaned_data['username']
        user = User.objects.get(username=username)
        if not user:
            form.add_error(None, 'Username not found')
            return self.form_invalid(form)

        ip = None
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')


        if not user.application.approved:
            form.add_error(None, 'Your application has not been approved by your sponsor yet. Please check later.')
            log_login_attempts(self.request.user.id, True, ip)
            return  self.form_invalid(form)

        response = super().form_valid(form)
        if self.request.user.is_authenticated:
            #return redirect('gdrp:dashboard')
            log_login_attempts(self.request.user.id, True, ip)
            return redirect('gdrp:dash_driver')
        else:
            pass
        
        log_login_attempts(self.request.user.id, False, ip)
        return response

# view for Sponsor group login
class SponsorLoginView(LoginView):
    template_name = "gdrp/Good_Driver.Sponsor_Login.html"
    context_object_name = "Sponsor Login"
    form_class = LoginForm
    
    def form_valid(self, form):
        ip = None
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')

        response = super().form_valid(form)
        if self.request.user.is_authenticated:
            #return redirect('gdrp:dashboard')
            log_login_attempts(self.request.user.id, True, ip)
            return redirect('gdrp:dash_sponsor')
        
        log_login_attempts(self.request.user.id, False, ip)
        return response

# view for admin group login
class AdminLoginView(LoginView):
    template_name = "gdrp/Good_Driver.Admin_Login.html"
    context_object_name = "Admin Login"
    form_class = LoginForm

    def form_valid(self, form):
        ip = None
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        
        response = super().form_valid(form)
        if self.request.user.is_authenticated:
            #return redirect('gdrp:dashboard')
            log_login_attempts(self.request.user.id, True, ip)
            return redirect('gdrp:dash_admin')
        

        def change_password(self, new_pwd):
            query = 'UPDATE admin SET pwd = %s WHERE user = %s'
            vals = (new_pwd, self.properties['user'])

        try:
            self.database.exec(query, vals)
        except Exception as e:
            raise Exception(e)

# view for admin to see all site users and log them out if needed
class AdminUserList(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = User
    template_name = "gdrp/user_list.html"
    context_object_name = "Users"
    login_url = 'gdrp:admin_login'

    def get_queryset(self):
        return User.objects.all().order_by('id')

    def test_func(self):
        isAdmin = self.request.user.groups.filter(name='admin').exists()
        isSponsor = self.request.user.groups.filter(name='Sponsors').exists()
        return isAdmin or isSponsor

# View for general account creation (unused)
class CreateAccount(generic.CreateView):
    form_class = AccountCreationForm
    template_name = "gdrp/create_account.html" 
    context_object_name = "Create Account"
    success_url = reverse_lazy('gdrp:driver_login')

# View for Dirvers group account creation
class CreateDriverAccount(generic.CreateView):
    form_class = DriverCreationForm
    template_name = "gdrp/create_account.html" 
    context_object_name = "Create Account"
    success_url = reverse_lazy('gdrp:driver_login')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.profile.refresh_token = ''
        sponsor = form.cleaned_data['sponsor']
        application = Application.objects.create(user=self.object, sponsor=sponsor)
        application.save()
        # call the log_account_creation function with the current user
        group = Group.objects.get(name="Drivers")
        self.object.groups.add(group)
        self.object.profile.SponsorID = sponsor
        self.object.save()
        log_application_sent(self.object.username, "Driver", "waiting approval")
        log_account_creation(self.object.username, "Driver")
        return response

# View for Sponsors group account creation 
class CreateSponsorAccount(generic.CreateView):
    form_class = SponsorCreationForm
    template_name = "gdrp/create_account.html" 
    context_object_name = "Create Account"
    success_url = reverse_lazy('gdrp:sponsor_login')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.profile.refresh_token = os.getenv('EBAY_TOKEN')
        sponsor = form.cleaned_data['sponsor']
        # call the log_account_creation function with the current user
        group = Group.objects.get(name="Sponsors")
        self.object.groups.add(group)
        self.object.profile.SponsorID = sponsor
        self.object.save()
        log_account_creation(self.object.username, "Sponsor")
        return response

# view for admin group account creation
class CreateAdminAccount(generic.CreateView):
    form_class = AdminCreationForm
    template_name = "gdrp/create_account.html" 
    context_object_name = "Create Account"
    success_url = reverse_lazy('gdrp:admin_login')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.profile.refresh_token = os.getenv('EBAY_TOKEN')
        # call the log_account_creation function with the current user
        group = Group.objects.get(name="admin")
        self.object.groups.add(group)
        self.request.user.is_staff = True
        self.object.save()
        log_account_creation(self.object.username, "Admin")
        return response


# view for changing a users password 
class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = "gdrp/change_pass.html"
    success_url = reverse_lazy('gdrp:dashboard')
    success_message = 'Your password has been changed.'

    def form_valid(self, form):
        response = super().form_valid(form)
        # call the log_password_change function with the current user
        log_password_change(self.request.user)
        return response

# view for reports page (unimplemented)
class ReportsView(generic.TemplateView):
    # This should probably be under a user specifc URL
    template_name = "gdrp/reports.html"
    context_object_name = "Reports"
    form_class = ReportsDriverPointsLogForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['EmailSponsorDriverPoints'] = ReportsDriverPointsLogForm()
        #context['another_form'] = AnotherForm()
        return context
    
    def post(self, request, *args, **kwargs):
        EmailSponsorDriverPoints = ReportsDriverPointsLogForm(request.POST)
        if EmailSponsorDriverPoints.is_valid():
            current_user = self.request.user
            cuser =  User.objects.get(id=current_user.id)
            sponsor_id = int(EmailSponsorDriverPoints.cleaned_data["SponsorID"])
            profiles = Profile.objects.filter(SponsorID=sponsor_id)
            users = [profile.user for profile in profiles]
            user_ids = [user.id for user in users]
            
            driverPointsLogForSponsor = points_filter(user_ids)
            
            emailBody = ''
            for row in driverPointsLogForSponsor:
                emailBody += f"{row['timestamp']},{row['user']},{row['points']}\n"
            
            send_mail(
                "[GDRP] Driver points activity for {}".format(sponsor_id),
                emailBody,
                "automated@gdrp.com",
                [cuser.email],
                fail_silently=False,
            )
            
        return self.render_to_response(self.get_context_data())
        
        

# view for logging out a user (used)
class UserLogoutView(LogoutView):
    next_page = reverse_lazy('gdrp:dashboard')

class CatalogView(generic.ListView):
    template_name = "gdrp/catalog.html"
    context_object_name = "products"

    def get_queryset(self):
        catalog = get_object_or_404(Catalog, pk=self.kwargs['catalog_id'])
        product_catalog = Product_catalog.objects.get(id=catalog.product_catalog.id)
        products = product_catalog.ProductIDs
        query = self.request.GET.get('q')
        page = self.request.GET.get('page', 1)

        if query:
            products = products.filter(name__icontains=query)
        else:
            products = product_catalog.ProductIDs.all()

        paginator = Paginator(products, 5)
        products = paginator.get_page(page)
        
        return products
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        catalog = get_object_or_404(Catalog, pk=self.kwargs['catalog_id'])
        product_catalog = Product_catalog.objects.get(id=catalog.product_catalog.id)
        page = self.request.GET.get('page', 1)
        context['catalog'] = catalog
        context['conversion_rate'] = catalog.conversion_rate
        context['sponsor'] = catalog.sponsor
        context['current_page'] = page
        #context['products'] = product_catalog.ProductIDs.all()
        return context

class CatalogSearchTagView(generic.ListView):
    template_name = "gdrp/catalog.html"
    context_object_name = "products"

    def get_queryset(self):
        catalog = get_object_or_404(Catalog, pk=self.kwargs['catalog_id'])
        product_catalog = Product_catalog.objects.get(id=catalog.product_catalog.id)
        products = product_catalog.ProductIDs.filter(tags__contains=self.kwargs['query'])
        return products
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        catalog = get_object_or_404(Catalog, pk=self.kwargs['catalog_id'])
        page = self.request.GET.get('page', 1)
        context['catalog'] = catalog
        context['conversion_rate'] = catalog.conversion_rate
        context['sponsor'] = catalog.sponsor
        context['current_page'] = page
        return context

class CatalogSearchCatView(generic.ListView):
    template_name = "gdrp/catalog.html"
    context_object_name = "products"

    def get_queryset(self):
        catalog = get_object_or_404(Catalog, pk=self.kwargs['catalog_id'])
        product_catalog = Product_catalog.objects.get(id=catalog.product_catalog.id)
        products = product_catalog.ProductIDs.filter(catagories__contains=self.kwargs['query'])
        return products
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        catalog = get_object_or_404(Catalog, pk=self.kwargs['catalog_id'])
        page = self.request.GET.get('page', 1)
        context['catalog'] = catalog
        context['conversion_rate'] = catalog.conversion_rate
        context['sponsor'] = catalog.sponsor
        context['current_page'] = page
        return context
    
class EbaySearch(LoginRequiredMixin, UserPassesTestMixin, generic.TemplateView):
    template_name = 'gdrp/ebay_search.html'
    login_url = 'gdrp/sponsor_login'

    def get(self, request):
        query = self.request.GET.get('q')
        page = self.request.GET.get('page', 1)
        api = EbayAPI()
        response = api.find(query)
        if response.total > 0:
            items = response.itemSummaries
            paginator = Paginator(items, 10)
            page_obj = paginator.get_page(page)

        context = {
            'q': query,
            'items': page_obj,
            'current_page': int(page)
        }
        return render(request, self.template_name, context)

    def test_func(self):
        isSponsor = self.request.user.groups.filter(name='Sponsors').exists()
        isAdmin = self.request.user.groups.filter(name='admin').exists()
        return isSponsor or isAdmin


class TeamInfoView(generic.TemplateView):
    template_name = "gdrp/contact.html"
    context_object_name = "contact"

class EditCatalogsView(UserPassesTestMixin, LoginRequiredMixin, generic.ListView):
    template_name = 'gdrp/edit_catalogs.html'
    context_object_name = 'catalogs'
    login_url = 'gdrp/admin_login'

    def get_queryset(self):
        return Catalog.objects.all()
    
    def post(self, request):
        cat_id = request.POST.get('cat_id')
        next = request.POST.get('next')
        Catalog.objects.delete(id=cat_id)

        return redirect('next')

    def test_func(self):
        isSponsor = self.request.user.groups.filter(name='Sponsors').exists()
        isAdmin = self.request.user.groups.filter(name='admin').exists()
        return isSponsor or isAdmin

# adds an item to the catalog
class AddToCatalog(generic.View):
    def post(self, request):
        api = EbayAPI()
        next = request.POST.get('next')
        user_id = request.POST.get('user_id')
        cat_id = request.POST.get('cat_id')
        item_id_raw = request.POST.get('item_id')
        item_id_list = item_id_raw.split('|')
        item_id = int("".join(item_id_list[1]))
        name = request.POST.get('item_name')
        price = request.POST.get('price')
        # currently unsure how to aquire item quantites or if that
        # is even a thing since we're working with ebay now 
        #inventory = request.POST.get('quantity')
        image = request.POST.get('image')
        item_spec = api.get_item(item_id_raw)
        category = item_spec.categoryPath
        tags = ''
        description = item_spec.description
        user = User.objects.get(id=user_id)
        sponsor = user.profile.SponsorID
        # create new catalog of cat_id if no catalog exsists
        if not Catalog.objects.filter(id=cat_id).exists():
            pc = Product_catalog.objects.create()
            # will need to update when we have sponsor system fleshed out
            catalog = Catalog.objects.create(id=cat_id, product_catalog=pc, sponsor_id=sponsor.id)
        else:
            catalog = Catalog.objects.get(id=cat_id)
        # points conversion 
        point_price = float(price) / catalog.conversion_rate

        if not item_id:
            return redirect(next)
        if not Product.objects.filter(id=item_id).exists():
            item = Product.objects.create(id=item_id, 
                                          name=name,
                                          description=str(description),
                                          price_dollars=price,
                                          price_points=point_price,
                                          image=image,
                                          categories=category,
                                          tags=str(tags))
            item.save()
        else:
            item = Product.objects.get(id=item_id)
        catalog.product_catalog.ProductIDs.add(item)
        catalog.save()
        return redirect(next)

def create_pdf(user_id, cost, item_id):
    # Create a new PDF file
    filename = f"{item_id}.pdf"
    pdf = canvas.Canvas(filename, pagesize=letter)

    # Add the user_id, cost, and item_id to the PDF file
    pdf.drawString(100, 750, f"User ID: {user_id}")
    pdf.drawString(100, 700, f"Cost: {cost}")
    pdf.drawString(100, 650, f"Item ID: {item_id}")

    # Save the PDF file
    pdf.save()

def download_pdf(request):
    if request.method == "POST":
        filename = request.POST.get('filename')
        with open(filename, 'rb') as f:
            response = FileResponse(f, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    
class PurchaseSingleItem(LoginRequiredMixin, generic.TemplateView):
    template_name = 'gdrp/catalog.html'

    def post(self, request):
        item_id = request.POST.get('item_id')
        user_id = request.user.id
        next = request.POST.get('next')
        item = Product.objects.get(id=item_id)
        user = User.objects.get(id=user_id)
        cost = item.price_points
        if cost <= user.profile.points:
            user.profile.points -= cost
            user.profile.save()
            create_pdf(user_id, cost, item_id)  # call create_pdf function
        else:
            messages.error(request, f"Not enough points")

        return redirect(next)

    
class AddToOrder(LoginRequiredMixin, generic.TemplateView):

    def post(self, request):
        item_id = request.POST.get('item_id')
        user_id = request.user.id
        next = request.POST.get('next')
        item = Product.objects.get(id=item_id)
        user = User.objects.get(id=user_id)
        if Order.objects.filter(UserID=user).exists():
            order = Order.objects.get(UserID=user)
        else:
            order = Order.objects.create(id=user.id, UserID=user, order_time=datetime.datetime.now()) 
        if Order_Details.objects.filter(OrderID=order).exists():
            cart = Order_Details.objects.get(OrderID=order)
        else:
            cart = Order_Details.objects.create(OrderID=order)
        cart.products.add(item)
        cart.quantity += 1
        order.point_total += item.price_points
        cart.save()
        order.save()
        # add logging here

        return redirect(next)
    
class Cart(LoginRequiredMixin, generic.ListView):
    template_name = 'gdrp/shoppingcart.html'

    # render list of items in cart
    def get(self, request):
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        if Order.objects.filter(UserID=user).exists():
            order = Order.objects.get(UserID=user)
            cart = Order_Details.objects.get(OrderID=order)
            items = cart.products.all()

            context = {
                'items': items,
                'order_id': order
            }

            return render(request, self.template_name, context)
        else:
            context = {
                'items': False,
                'oder_id': False
            }
            return render(request, self.template_name, context)

    # for placing order
    def post(self, request):
        next = request.POST.get('next')
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        order = Order.objects.get(UserID=user)
        cost = order.point_total
        if cost <= user.profile.points:
            user.profile.points -= cost
            order.delete()
            user.save()
        else:
            messages.error(request, "Not enough points")

        return redirect(next)
    
class ReportAndLogView(generic.TemplateView):
    template_name='gdrp/auditlogdownload.html'

# class to logout a user (unused)
def logout_user(request, user_id):
    user = User.objects.get(id=user_id)
    session_key = Session.objects.filter(
        session_key__startswith=f"_auth_user_id_={user.id}"
    ).values_list('session_key', flat=True).first()
    if session_key:
        session = Session.objects.get(session_key=session_key)
        session.delete()

    #print(request)
    #logout(request, user)
    return redirect('gdrp:dashboard')

def add_points(request, user_id):
    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        points = int(request.POST.get('num_points', 0))
        user.profile.points += points
        log_points_added(user, points)
        user.profile.save()
        return redirect('gdrp:user_list')

def remove_points(request, user_id):
    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        points = int(request.POST.get('num_points', 0))
        user.profile.points -= points
        log_points_removed(user, -points)
        user.profile.save()
        return redirect('gdrp:user_list')

def zero_points(request, user_id):
    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        user.profile.points = 0
        log_points_added(user, -user.profile.points)
        user.profile.save()
        return redirect('gdrp:user_list')

# view method for processing order 
# currently just removes the order total from the users points
def process_order(request, order_id):
    order = Order.objects.get(id=order_id)
    user = order.UserID
    total = order.point_total
    user.profile.points -= total
    user.profile.save()
    return redirect('gdrp:oder')

def change_point_conversion(request, catalog_id):
    catalog = Catalog.objects.get(id=catalog_id)
    if request.method == 'POST':
        new_rate = float(request.POST.get('conversion_rate', 0.001))
        catalog.conversion_rate = new_rate
        catalog.save()
        return redirect('gdrp:dashboard')
    
# sets so points go higher than set max
def max_points(request, user_id): 
    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        points = int(request.POST.get('num_points', 99999999))
        log_points_added(user, points)
        user.profile.points == points
        user.profile.save()
        return redirect('gdrp:user_list')

def download_logs(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')

    with open("password_changes.csv", mode="r") as password_changes_csv_file, \
         open("account_creations.csv", mode="r") as account_creations_csv_file, \
         open("login_attempts.csv", mode="r") as login_attempts_csv_file, \
         open("points_log.csv", mode="r") as points_log_csv_file, \
         open("catalog_log.csv", mode="r") as catalog_log_csv_file:
        
        # read password_changes.csv
        password_changes_reader = csv.DictReader(password_changes_csv_file)
        password_changes_rows_to_download = []
        for row in password_changes_reader:
            row_timestamp = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            if start_date <= row_timestamp <= end_date:
                password_changes_rows_to_download.append(row)

        # read account_creations.csv
        account_creations_reader = csv.DictReader(account_creations_csv_file)
        account_creations_rows_to_download = []
        for row in account_creations_reader:
            row_timestamp = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            if start_date <= row_timestamp <= end_date:
                account_creations_rows_to_download.append(row)

        # read login_attempts.csv
        login_attempts_reader = csv.DictReader(login_attempts_csv_file)
        login_attempts_rows_to_download = []
        for row in login_attempts_reader:
            row_timestamp = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            if start_date <= row_timestamp <= end_date:
                login_attempts_rows_to_download.append(row)
        
        # read points_log.csv
        points_log_reader = csv.DictReader(points_log_csv_file)
        rows_to_download = []
        for row in points_log_reader:
            timestamp = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            if start_date <= timestamp.date() <= end_date:
                row["timestamp"] = timestamp.strftime("%m/%d/%Y %H:%M:%S")
                rows_to_download.append(row)
        
        # read catalog_log.csv
        catalog_log_reader = csv.DictReader(catalog_log_csv_file)
        for row in catalog_log_reader:
            timestamp = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            if start_date <= timestamp.date() <= end_date:
                row["timestamp"] = timestamp.strftime("%m/%d/%Y %H:%M:%S")
                rows_to_download.append(row)

    # check if there are any logs to download
    if not password_changes_rows_to_download and not account_creations_rows_to_download and not login_attempts_rows_to_download:
        return HttpResponse("No logs found within specified date range.")

    # create the CSV file for the logs to download
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="logs.csv"'

    fieldnames = ["log_type", "user", "timestamp", "details"]
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    # write the password_changes logs to the CSV file
    for row in password_changes_rows_to_download:
        writer.writerow({"log_type": "password_changes", "user": row["user"], "timestamp": row["timestamp"], "details": f'Total password changes: {row["password_changes"]}'})

    # write the account_creations logs to the CSV file
    for row in account_creations_rows_to_download:
        writer.writerow({"log_type": "account_creations", "user": row["user"], "timestamp": row["timestamp"], "details": f'{row["user_type"]} account created'})

    # write the login_attempts logs to the CSV file
    for row in login_attempts_rows_to_download:
        writer.writerow({"log_type": "login_attempts", "user": row["user"], "timestamp": row["timestamp"], "details": f'Login {row["result"]}'})
    
    # write the points_log and catalog_log logs to the CSV file
    for row in rows_to_download:
        writer.writerow({
        "log_type": row["log_type"],
        "user": row["user"],
        "timestamp": row["timestamp"],
        "details": row["details"]
    })

    return response

def download_account_creations(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')

    generate_account_creation_report()

    with open("account_creations.csv", mode="r") as account_creations_csv_file:
        
        # read account_creations.csv
        account_creations_reader = csv.DictReader(account_creations_csv_file)
        account_creations_rows_to_download = []
        for row in account_creations_reader:
            row_timestamp = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            if start_date <= row_timestamp <= end_date:
                account_creations_rows_to_download.append(row)

    # check if there are any logs to download
    if not account_creations_rows_to_download:
        return HttpResponse("No logs found within specified date range.")

    # create the CSV file for the logs to download
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="acct_create_logs.csv"'

    fieldnames = ["log_type", "user", "timestamp", "details"]
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    # write the account_creations logs to the CSV file
    for row in account_creations_rows_to_download:
        writer.writerow({"log_type": "account_creations", "user": row["user"], "timestamp": row["timestamp"], "details": f'{row["user_type"]} account created'})

    return response

def download_account_deletions(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')

    generate_account_deletion_report()

    with open("account_deletions.csv", mode="r") as account_deletions_csv_file:
        
        # read account_creations.csv
        account_deletions_reader = csv.DictReader(account_deletions_csv_file)
        account_deletions_rows_to_download = []
        for row in account_deletions_reader:
            row_timestamp = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            if start_date <= row_timestamp <= end_date:
                account_deletions_rows_to_download.append(row)

    # check if there are any logs to download
    if not account_deletions_rows_to_download:
        return HttpResponse("No logs found within specified date range.")

    # create the CSV file for the logs to download
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="acct_delete_logs.csv"'

    fieldnames = ["log_type", "user", "timestamp", "details"]
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    # write the account_creations logs to the CSV file
    for row in account_deletions_rows_to_download:
        writer.writerow({"log_type": "account_deletions", "user": row["user"], "timestamp": row["timestamp"], "details": f'{row["user_type"]} account deleted'})

    return response

def download_password_changes(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')

    # generate password change report
    generate_password_change_report(start_date, end_date)

    # create the CSV file for the logs to download
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="pass_change_logs.csv"'

    # write the password_changes logs to the CSV file
    with open("password_changes.csv", mode="r") as password_changes_csv_file:
        password_changes_reader = csv.DictReader(password_changes_csv_file)
        fieldnames = ["log_type", "user", "timestamp", "details"]
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()

        for row in password_changes_reader:
            row_timestamp = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            if start_date <= row_timestamp <= end_date:
                writer.writerow({"log_type": "password_changes", "user": row["user"], "timestamp": row["timestamp"], "details": f'Total password changes: {row["password_changes"]}'})
    
    return response

def download_login_attempts(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')

    # generate login attempt report
    generate_login_attempt_report(start_date, end_date)

    # create the CSV file for the logs to download
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="login_attempt_logs.csv"'

    # write the login attempts logs to the CSV file
    with open("login_attempts.csv", mode="r") as login_attempts_csv_file:
        login_attempts_reader = csv.DictReader(login_attempts_csv_file)
        fieldnames = ["log_type", "user", "timestamp", "details"]
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()

        for row in login_attempts_reader:
            row_timestamp = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            if start_date <= row_timestamp <= end_date:
                writer.writerow({"log_type": "login_attempts", "user": row["user"], "timestamp": row["timestamp"], "details": f'Login status: {row["status"]}'})
    
    return response

def download_points_added(request):
    user = request.GET.get('user')
    points = request.GET.get('points')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("points_log.csv", mode="r") as csv_file:
        # read the existing data from the CSV file
        fieldnames = ["timestamp", "user", "points"]
        reader = csv.DictReader(csv_file, fieldnames=fieldnames)
        points_added_rows = list(reader)

    # add the new points added log
    log_message = f"{timestamp}: {points} points added to {user}."
    points_added_rows.append({"timestamp": timestamp, "user": user, "points": points})

    # write the updated data to the CSV file
    with open("points_log.csv", mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(points_added_rows)
    
    return HttpResponse(f"{points} points added to {user} at {timestamp}")

def download_points_removed(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
    with open("points_log.csv", mode="r") as points_log_csv_file:
        
        # read points_log.csv
        points_log_reader = csv.DictReader(points_log_csv_file)
        points_log_rows_to_download = []
        for row in points_log_reader:
            row_timestamp = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            if start_date <= row_timestamp <= end_date and int(row["points"]) < 0:
                points_log_rows_to_download.append(row)

    # check if there are any logs to download
    if not points_log_rows_to_download:
        return HttpResponse("No logs found within specified date range.")

    # create the CSV file for the logs to download
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="points_removed.csv"'

    fieldnames = ["log_type", "user", "timestamp", "points"]
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    # write the points_removed logs to the CSV file
    for row in points_log_rows_to_download:
        writer.writerow({"log_type": "points_removed", "user": row["user"], "timestamp": row["timestamp"], "points": row["points"]})

    return response
def download_catalog_changes(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
    with open("catalog_log.csv", mode="r") as catalog_log_csv_file:
        
        # read catalog_log.csv
        catalog_log_reader = csv.DictReader(catalog_log_csv_file)
        catalog_rows_to_download = []
        for row in catalog_log_reader:
            row_timestamp = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            if start_date <= row_timestamp <= end_date:
                catalog_rows_to_download.append(row)

    # check if there are any logs to download
    if not catalog_rows_to_download:
        return HttpResponse("No logs found within specified date range.")

    # create the CSV file for the logs to download
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="catalog_changes.csv"'

    fieldnames = ["log_type", "name", "price", "timestamp", "action"]
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    # write the catalog logs to the CSV file
    for row in catalog_rows_to_download:
        writer.writerow({"log_type": "catalog_changes", "name": row["name"], "price": row["price"], "timestamp": row["timestamp"], "action": row["action"]})

    return response

def download_application_sent(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')

    generate_application_sent_report(start_date, end_date)

    with open("application_log.csv", mode="r") as application_sent_csv_file:
        
        # read account_creations.csv
        application_sent_reader = csv.DictReader(application_sent_csv_file)
        application_sent_rows_to_download = []
        for row in application_sent_reader:
            row_timestamp = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            if start_date <= row_timestamp <= end_date:
                application_sent_rows_to_download.append(row)

    # check if there are any logs to download
    if not application_sent_rows_to_download:
        return HttpResponse("No logs found within specified date range.")

    # create the CSV file for the logs to download
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="application_log.csv"'

    fieldnames = ["log_type", "user", "timestamp", "details"]
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    # write the account_creations logs to the CSV file
    for row in application_sent_rows_to_download:
        writer.writerow({"log_type": "application_sent", "user": row["user"], "timestamp": row["timestamp"], "details": f'application sent'})

    return response

# testing out generating auth tokens for ebay
def auth(request):
    api = Trading(domain='api.sandbox.ebay.com',
                  debug=True,
                  appid=settings.EBAY_APPID,
                  devid=settings.EBAY_DEVID,
                  certid=settings.EBAY_CERID,
                  config_file=None)
    
    request = {'RuName': 'Alexander_Tedro-Alexande-Team04-bvmovyccu'}
    response = api.execute('GetSessionID', request)
    auth_url = 'https://signin.sandbox.ebay.com/ws/eBayISAPI.dll?SignIn&runame={}&SessID={}'.format('Alexander_Tedro-Alexande-Team04-bvmovyccu', response.reply.SessionID)
    return redirect(auth_url)
# callback function for ebay token auth
def auth_callback(request):

    api = Trading(domain='api.sandbox.ebay.com',
                  debug=True,
                  appid=settings.EBAY_APPID,
                  devid=settings.EBAY_DEVID,
                  certid=settings.EBAY_CERID,
                  config_file=None)
    request = {
        'RequestToken': request.GET.get('ebaytkn'),
        'ErrorLanguage': 'en_US'
    }
    response = api.execute('FetchToken', request)
    user, created = User.objects.get_or_create(username=response.reply.eBayUser, defaults={'refresh_token': response.reply.eBayAuthToken})
    if not created:
        user.refresh_token = response.reply.eBayAuthToken
        user.save()
    return redirect('gdrp/dashboard')

def remove_item_catalog(request):
    item_id = request.POST.get('item_id') 
    cat_id = request.POST.get('cat_id')
    next = request.POST.get('next')
    print(item_id)
    item = Product.objects.get(id=int(item_id))
    catalog = Catalog.objects.get(pk=cat_id)
    catalog.product_catalog.ProductIDs.remove(item)

    return redirect(next)

def approve_application(request):
    if request.method == 'POST':
        user = request.POST.get('user')
        application = Application.objects.get(user=user)
        application.approved = True
        application.save()

        return redirect('gdrp:dash_sponsor')
    
def change_conv_rate(request):
    if request.method == "POST":
        next = request.POST.get('next')
        cat_id = request.POST.get('cat_id')
        new_rate = request.POST.get('new_rate')
        catalog = Catalog.objects.get(pk=cat_id)
        catalog.conversion_rate = new_rate
        catalog.save()

        # update point prices for all items in catalog
        items = catalog.product_catalog.ProductIDs.all()

        for item in items:
            product = Product.objects.get(id=item.id)
            product.price_points = float(product.price_dollars) / float(catalog.conversion_rate)
            product.save()

        return redirect(next)
