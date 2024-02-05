from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'
urlpatterns = [
    path(route='home/', view=views.my_home_view, name='my_home_view'),    
    path(route='about/', view=views.about, name='about'),    
    path(route='contact/', view=views.contact, name='contact'),
    # Authentication related urls
    path(route='registration/', view=views.registration_request, name='registration'),
    path(route='login/', view=views.login_request, name='login'),
    path(route='logout/', view=views.logout_request, name='logout'),
    
    path(route='', view=views.get_dealerships, name='index'),
    path(route='<int:dealer_id>/', view=views.get_dealer_details, name='index'),

    # path for dealer reviews view

    # path for add a review view

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)