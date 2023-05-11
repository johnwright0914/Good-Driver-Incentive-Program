from django.contrib import admin

from .models import *
# Register your models here.

admin.site.register(Product)
admin.site.register(Catalog)
admin.site.register(Sponsor)
admin.site.register(Profile)