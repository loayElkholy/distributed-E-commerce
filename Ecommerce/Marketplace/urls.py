from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static
urlpatterns =[
    path('' ,views.index ,name="index" ),
    path('login' ,views.login ,name="login"),
    path('register' ,views.register ,name="register"),
    path('product/<int:id>',views.product ,name="product"),
    path('category/<str:cat>' ,views.category ,name="category"),
    path('logout',views.logout , name='logout'),
    path('dashboard',views.dashboard ,name='dashboard') ,
    path('cart',views.cart ,name='cart') ,
    path('addreview/<int:id>',views.addreview ,name='addreview') ,
    path('changequantity/<int:id>',views.changequantity ,name='changequantity') ,
    path('changecurrency/<int:id>',views.changecurrency ,name='changecurrency') ,
    path('my_sales/', views.my_sales, name='my_sales'),
    path('my_purchases/', views.my_purchases, name='my_purchases'),
    path('my_profile/', views.my_profile, name='my_profile'),
    path('addtocart/<int:id>',views.addtocart  , name='addtocart')]


urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
