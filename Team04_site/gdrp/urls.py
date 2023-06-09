from django.urls import path
from . import views
import datetime


app_name = 'gdrp'
urlpatterns = [
    path('', views.HomepageView.as_view(), name="homepage"),
    path('privacy_policy/', views.PrivacyPolicyView.as_view(), name="privacy_policy"),
    path('termsofservice/', views.ToSView.as_view(), name="tos"),
    path('contact/', views.TeamInfoView.as_view(), name='contact'),
    path('about/', views.TeamInfoView.as_view(), name='about'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/driver/', views.DriverDashboardView.as_view(), name='dash_driver'),
    path('promotions/create/', views.PromotionCreateView.as_view(), name='promo_create'),
    path('dashboard/admin/', views.AdminDashboardView.as_view(), name='dash_admin'),
    path('dashboard/sponsor/', views.SponsorDashboardView.as_view(), name='dash_sponsor'),
    path('account/', views.UserInfo.as_view(), name='account_info'),
    path('account/login/', views.UserLoginView.as_view(), name='account_login'),
    path('product/<int:pk>/', views.ProductView.as_view(), name='product'),
    path('add_products/', views.AddProductsFormView.as_view(), name='product_addm'),
    path('remove_products/', views.remove_item_catalog, name="remove_item"),
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('user_login/', views.UserLoginView.as_view(), name='user_login'),
    path('driver_login/', views.DriverLoginView.as_view(), name='driver_login'),
    path('sponsor_login/', views.SponsorLoginView.as_view(), name='sponsor_login'),
    path('admin_login/', views.AdminLoginView.as_view(), name='admin_login'),
    path('user_list/', views.AdminUserList.as_view(), name='user_list'),
    path('create_account/', views.CreateAccount.as_view(), name='create_account'),
    path('create_account/driver/', views.CreateDriverAccount.as_view(), name='create_driver'),
    path('create_account/sponsor/', views.CreateSponsorAccount.as_view(), name='create_sponsor'),
    path('create_account/admin/', views.CreateAdminAccount.as_view(), name='create_admin'),
    path('sponsor_create/', views.SponsorCreateView.as_view(), name='sponsor_create'),
    path('sponsor_create/login', views.AdminLoginView.as_view(), name='spc_admin_login'),
    path('catalog/<int:catalog_id>/', views.CatalogView.as_view(), name='catalog'),
    path('edit_catalogs/', views.EditCatalogsView.as_view(), name='edit_catalogs'),
    #path('catalog/<int:catalog_id>/search_tag/<str:query>/', views.CatalogSearchTagView.as_view(), name='catalog_tag_search'),
    #path('catalog/<int:catalog_id>/search_cat/<str:query>/', views.CatalogSearchCatView.as_view(), name='catalog_cat_search'),
    path('ebay_search/', views.EbaySearch.as_view(), name='ebay_search'),
    path('ebay_search/add/', views.AddToCatalog.as_view(), name="add_to_catalog"),
    path('change_pass/', views.ChangePasswordView.as_view(), name='change_pass'),
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('logs/', views.ReportAndLogView.as_view(), name='reports_logs'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('logout_user/<int:user_id>/', views.logout_user, name='logout_user'),
    path('user_list/add_points/<int:user_id>/', views.add_points, name='add_points'),
    path('user_list/remove_points/<int:user_id>/', views.remove_points, name='remove_points'),
    path('user_list/zero_points/<int:user_id>/', views.zero_points, name='zero_points'),
    path('process_order/<int:order_id>/', views.process_order, name='process_order'),
    path('change_pointc/<int:catalog_id>/', views.change_point_conversion, name='change_point_converion'),
    path('max_points/<int:user_id>/', views.max_points, name='max_points'),
    path('download_logs/', views.download_logs, name='download_logs'),
    path('download-login-attempts/', views.download_login_attempts, name='download_login_attempts'),
    path('download-account-creations/', views.download_account_creations, name='download_account_creations'),
    path('download-password-changes/', views.download_password_changes, name='download_password_changes'),
    path('download-points-removed/', views.download_points_removed, name='download_points_removed'),
    path('download-points-added/', views.download_points_added, name='download_points_added'),
    path('download-application-sent/', views.download_application_sent, name='download_application_sent'),
    path('download-account-deletions/', views.download_account_deletions, name='download_account_deletions'),
    path('download_pdf/', views.download_pdf, name='download_pdf'),
    # path('download-catalog-changes/', views.download_catalog_changes, name ='download_catalog_changes'),
    path('auth/', views.auth, name='auth'),
    path('auth/callback/', views.auth_callback, name='auth_callback'),
    path('quick_pruchase/', views.PurchaseSingleItem.as_view(), name='single_buy'),
    path('add_to_cart/', views.AddToOrder.as_view(), name="add_to_order"),
    path('shopping_cart/', views.Cart.as_view(), name='shoppingcart'),
    path('approve_application/', views.approve_application, name='approve_application'),
    path('download_pdf/<str:filename>/', views.download_pdf, name='download_pdf'),
    path('change_conv_rate/', views.change_conv_rate, name='change_conv_rate'),
]
