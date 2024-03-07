import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
import os

# Create a `get_request` to make HTTP GET requests
def get_request(url, **kwargs):    
    api_key=""
    try:        
        if api_key:                                   
            response = requests.get(url, params=kwargs, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:            
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
        return {}
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)    
    return json_data

# Create a `post_request` to make HTTP POST requests
def post_request(url, json_payload):
    print("Data to be posted : ", json_payload)
    print("Post URL: ", url)    
    response = requests.post(url, json=json_payload)
    print("post_request response: ", response)
    return response

# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer            
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results

def get_dealers_by_id(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, id=dealerId)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealer_id):
    reviews_data = get_request(url, id=dealer_id)
    
    if reviews_data is None:
        return None
    
    # Convert the JSON result into a list of DealerReview objects
    results = []
    
    for review_data in reviews_data:
       
        result = DealerReview(
            dealership=review_data.get('dealership'),
            name=review_data.get('name'),
            purchase=review_data.get('purchase'),
            review=review_data.get('review'),
            purchase_date=review_data.get('purchase_date'),
            car_make=review_data.get('car_make'),
            car_model=review_data.get('car_model'),
            car_year=review_data.get('car_year'),
            sentiment=review_data.get('sentiment'),
            id=review_data.get('id')
        )
        result.sentiment = analyze_review_sentiments(result.review)        
        results.append(result)    
    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
    url = "https://api.eu-de.natural-language-understanding.watson.cloud.ibm.com/instances/bb1a1074-1c00-4c14-a794-bf8c2f64c064"
    api_key = "uXj_a3Qjyb9QCyU4FYrMEh7YVjPnQ8Iz9nKRMWZXzghy"
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator)
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze( text=text+"hello hello hello",features=Features(sentiment=SentimentOptions(targets=[text+"hello hello hello"]))).get_result()
    label=json.dumps(response, indent=2)
    label = response['sentiment']['document']['label']    
    return(label)