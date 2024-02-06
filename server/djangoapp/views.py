from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
# from .models import related models
from .restapis import get_dealers_from_cf, get_dealers_by_id,get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/user_registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/user_registration.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            print("logged in ....")
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)


def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')
    
# Create your views here.
def my_home_view(request):
    return render(request, 'djangoapp/home.html')

# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    company_address = "2150 Ogden Ave,Downers Grove,IL 60515"
    telephone_number = "+1234567890"

    context = {
        'company_address': company_address,
        'telephone_number': telephone_number,
    }

    return render(request, 'djangoapp/contact.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        #url = "https://sruthiravuru-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        url = ""
        if not url:
            return render(request, 'djangoapp/index.html')

        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        #dealerships = get_dealers_by_id(url, )        
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    print(dealer_id)
    reviews_url = "https://sruthiravuru-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
    
    # Call get_dealer_reviews_from_cf method to get reviews for the dealer_id
    dealer_reviews = get_dealer_reviews_from_cf(reviews_url, dealer_id)
    
    if dealer_reviews is None:
        return HttpResponse("Failed to fetch dealer reviews", status=500)
    
    # Append the list of reviews to context
    context = {
        'dealer_id': dealer_id,
        'dealer_reviews': dealer_reviews
    }
    
    # Return a HttpResponse with the context
    return HttpResponse(context)


# Create a `add_review` view to submit a review
@login_required
def add_review(request, dealer_id):
    request.method = 'POST'  
    if request.method == 'POST':
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return HttpResponse("Unauthorized", status=401)
        
        # Create a dictionary object called review
        review = {}
        review["time"] = datetime.utcnow().isoformat()
        review["name"] = request.user.username  # Assuming user name is the authenticated user's username
        review["dealership"] = dealer_id
        review["review"] = request.POST.get('review_text', '')
        #review["purchase"] = request.POST.get('purchase', '')

        # Create a JSON payload with the review
        json_payload = {}
        json_payload["review"] = review

        # Assuming you have the URL for posting reviews
        post_reviews_url = "https://sruthiravuru-8000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/djangoapp/review/"
        
        # Make a POST request to add the review
        post_response = post_request(post_reviews_url, json_payload, dealer_id=dealer_id)

        if post_response.status_code == 201:
            return HttpResponse("Review added successfully", status=201)
        else:
            return HttpResponse(f"Failed to add review: {post_response.text}", status=500)
    else:
        return HttpResponse("Method not allowed", status=405)

