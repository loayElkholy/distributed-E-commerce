from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login 
from django.contrib.auth import logout as auth_logout 
from django.shortcuts import render, redirect
from django.contrib.auth.forms import  UserCreationForm

from .models import *



def index(request):
    if "orders" not in request.session:
        request.session["orders"] = []
        request.session["currency"] = {"currencyName": "USD", "value":1 }
    if request.method == "POST":
        products = Product.objects.filter(name=request.POST["search"].lower())
        return render(request, 'Marketplace/index.html', {
            "products": products,
            "message": "Search results"
        })
    else:

        return render(request, 'Marketplace/index.html', {
            "products": Product.objects.all(),
            "message": "Shop all products"
        })





def login (request):
    if(not request.user.is_authenticated ):
        if request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request,user)
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, 'Marketplace/login.html',{
                    "message":"wrong username or password"
                })
        return render(request, 'Marketplace/login.html')
    else :
        return HttpResponseRedirect(reverse("index"))


def register(request):
    if(not request.user.is_authenticated):
        form = UserCreationForm()
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                user_data = User.objects.get(username=form.cleaned_data["username"])
                auth_login(request,user_data)
                if(request.POST["usertype"]=="option2"):
                    seller =Seller(user=user_data ,email=request.POST["email"])
                    seller.save()
                else:
                    customer =Customer(user=user_data ,email=request.POST["email"])
                    customer.save()
                return HttpResponseRedirect(reverse("index"))
        context = {'form': form}
        return render(request, 'Marketplace/register.html', context)
    else:
        return HttpResponseRedirect(reverse("index"))



def product(request, id):
    if request.method == "POST":
        review = request.POST["review"]
    product = Product.objects.get(id=id)
    category = product.category
    reviews = Review.objects.filter(product=id)
    similar_products = Product.objects.filter(category=category).exclude(id=id)
    return render(request, 'Marketplace/product.html', {
        'product': product,
        'reviews': reviews,
        "similar_products": similar_products
    })



def category(request, cat):
    return render(request, 'Marketplace/index.html', {
            "products": Product.objects.filter(category=cat), "message": f"{cat} category "
        })



def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse("index"))



def dashboard(request):
    try:
        seller_id = request.user.seller.id
    except:
        return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        product = Product(seller=request.user.seller, name=request.POST["name"],
                          price=request.POST["price"], category=request.POST["category"],
                          image=(request.FILES["image"]), stock=request.POST["stock"])
        product.save() 
        products = Product.objects.filter(seller=seller_id)
        return render(request, 'Marketplace/dashboard.html', {'products': products})
    else:
        products = Product.objects.filter(seller=seller_id)
        return render(request, 'Marketplace/dashboard.html', {
            'products': products
    })



def addtocart(request, id):
    if request.session["orders"]:
        flag =0
        for i in range(len(request.session["orders"])):
            if request.session["orders"][i]["product_id"] == id :
                flag =1
                quantity =request.session["orders"][i]["quantity"] +int(request.POST["quantity"])
                request.session["orders"].pop(i)
                request.session["orders"] += [{"product_id": id, "quantity": quantity}]
        if flag ==0 :
            request.session["orders"] += [{"product_id": id, "quantity": int(request.POST["quantity"])}]
    else: 
        request.session["orders"] += [{"product_id": id, "quantity": int(request.POST["quantity"])}]
    return HttpResponseRedirect(reverse("index"))



def cart(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
        cart = Checkout(seller=Seller.objects.get(user=request.user), payment_method=request.POST["paymentMethod"])
        cart.save()
        for orders in request.session["orders"]:
            product_id = orders["product_id"]
            quantity = orders["quantity"]
            buyer=Seller.objects.get(user=request.user)
            seller=Product.objects.get(id=product_id).seller
            buyer.money=buyer.money-Product.objects.get(id=product_id).price*quantity
            seller.money=seller.money+Product.objects.get(id=product_id).price*quantity
            buyer.save()
            seller.save()
            Order(product=Product.objects.get(id=product_id), quantity=quantity, checkout=cart).save()
            Purchase(product=Product.objects.get(id=product_id),seller=Product.objects.get(id=product_id).seller,buyer=request.user).save()  ### save purchase
            return HttpResponseRedirect(reverse("index"))
    else:
        user_cart = []
        total = 0
        for order in request.session["orders"]:
            product_id = order['product_id']
            quantity = order['quantity']
            total += Product.objects.get(id=product_id).price *quantity
            user_cart.append([Product.objects.get(id=product_id), quantity])
        total= total*request.session["currency"]["value"]
        return render(request, 'Marketplace/cart.html', {
            'cart': user_cart ,
            "total" : total})



def addreview(request, id):
    if request.user.is_authenticated:
        product =Product.objects.get(id=id)
        user= Seller.objects.get(user=request.user)
        if not Review.objects.filter(seller=user).filter(product=id) :
            Review(seller=user, review=request.POST["review"], product=product).save()
        else:
            r= Review.objects.filter(Seller=user.id).get(product=id)
            r.review=request.POST["review"]
            r.save()
        return HttpResponseRedirect(reverse("index"))
    else :
        return HttpResponseRedirect(reverse("login"))

def changequantity(request,id):
    for order in request.session["orders"]: 
        if order["product_id"] ==id:
            if not int(request.POST["quantity"]) ==0:
                request.session["orders"].remove(order) 
                request.session["orders"] += [{"product_id": id, "quantity": int(request.POST["quantity"])}]
            else:
                request.session["orders"].remove(order) 
                request.session["orders"] =request.session["orders"]+[]
 

    return HttpResponseRedirect(reverse("cart"))

    
            
def changecurrency(request ,id):
    if not (id ==request.session["currency"]["value"]):
        if id ==15 :
            request.session["currency"] = {"currencyName": "EGP","value":15}
            for product in Product.objects.all():
                product.price = round(product.price*15)
                product.save()
        else:
            request.session["currency"] = {"currencyName": "USD","value":1}
            for product in Product.objects.all():
                product.price = round(product.price/15)
                product.save()
    return HttpResponseRedirect(reverse("index"))

def my_sales(request):
    seller_id = request.user.seller.id
    purchases=Purchase.objects.all().filter(seller=seller_id)
    return render(request, 'Marketplace/my_sales.html', {"purchases": purchases})


def my_purchases(request):
    purchases = Purchase.objects.filter(buyer=request.user)
    return render(request, 'Marketplace/my_purchases.html', {"purchases": purchases})

def my_profile(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if request.method == 'POST':
        seller= Seller.objects.get(user=request.user)
        seller.money= int(request.POST["money"])+seller.money
        seller.save()
        return render(request, 'Marketplace/my_profile.html', {"seller": seller}) 
    seller= Seller.objects.get(user=request.user)
    return render(request, 'Marketplace/my_profile.html', {"seller": seller})



def make_purchase(request):
    if request.method == 'POST' and request.user.is_anonymous():
        try:
            product = Product.objects.get(id=request.POST['product_id'])
        except Product.DoesNotExist:
            return redirect('login')

    return redirect('login')
