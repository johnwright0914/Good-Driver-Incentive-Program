from django.contrib.auth.models import User
from .models import Catalog

def get_catalogs(request):
    user = request.user
    if user.is_authenticated:
        catalog_sponsor = Catalog.objects.filter(sponsor=user.profile.SponsorID)
    else:
        catalog_sponsor = Catalog.objects.all()
    return { 
        'catalogs_sponsor': catalog_sponsor,
        'catalogs': Catalog.objects.all()
        }

