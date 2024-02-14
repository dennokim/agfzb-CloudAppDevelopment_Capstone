import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features,SentimentOptions
import time

def get_request(url, **kwargs):
    api_key = kwargs.get("api_key")
    print("GET from {} ".format(url))
    
    try:
        if api_key:
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except requests.RequestException as e:
        # If any error occurs during the request
        print(f"Network exception occurred: {e}")
        return None

    status_code = response.status_code
    print("With status {} ".format(status_code))

    if response.text:
        try:
            json_data = json.loads(response.text)
            return json_data
        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None
    else:
        # Handle empty response
        print("Empty response received")
        return None


def post_request(url, payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    print(payload)
    response = requests.post(url, params=kwargs, json=payload)
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in 'doc' object
            dealer_doc = dealer
            # Create a CarDealer object with values in 'doc' object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                  id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"], short_name=dealer_doc["short_name"],
                                  st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
        return results


def get_dealer_by_id_from_cf(url, id):
    json_result = get_request(url, id=id)
    print('json_result from line 54', json_result)

    if json_result and isinstance(json_result, list) and len(json_result) > 0:
        dealer_doc = json_result[0]
        dealer_obj = CarDealer(
            address=dealer_doc.get("address", ""),
            city=dealer_doc.get("city", ""),
            id=dealer_doc.get("id", ""),
            lat=dealer_doc.get("lat", ""),
            long=dealer_doc.get("long", ""),
            full_name=dealer_doc.get("full_name", ""),
            st=dealer_doc.get("st", ""),
            zip=dealer_doc.get("zip", "")
        )
        return dealer_obj
    else:
        # Handle errors, for example:
        print("Error: Invalid or empty response.")
        return None



def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    id = kwargs.get("id")
    
    if id:
        json_result = get_request(url, id=id)
    else:
        json_result = get_request(url)
    
    # Check if the response is a string
    if isinstance(json_result, str):
        print("Error: API response is a string, not JSON.")
        return results
    
    try:
        # Assuming the expected structure, if "data" and "docs" are present
        reviews = json_result.get("data", {}).get("docs", [])
        
        for dealer_review in reviews:
            review_obj = DealerReview(dealership=dealer_review.get("dealership", ""),
                                   name=dealer_review.get("name", ""),
                                   purchase=dealer_review.get("purchase", ""),
                                   review=dealer_review.get("review", ""))
            
            # Extract other attributes accordingly
            
            sentiment = analyze_review_sentiments(review_obj.review)
            review_obj.sentiment = sentiment
            results.append(review_obj)
    except Exception as e:
        print(f"Error processing JSON response: {e}")
        if isinstance(json_result, str):
            print(f"API response (string): {json_result}")
            print("Error: API response is a string, not JSON.")
        return results



def analyze_review_sentiments(text):
    url = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/a7d55b2b-30e4-4d58-91a1-bd84cb7b5c14"
    api_key = "S8Ncd3903aq7KoTo6MJPqi3nrpIvivQuWJdwqmMQifFK"
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator)
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze( text=text+"hello hello hello",features=Features(sentiment=SentimentOptions(targets=[text+"hello hello hello"]))).get_result()
    label=json.dumps(response, indent=2)
    label = response['sentiment']['document']['label']
    
    
    return(label)