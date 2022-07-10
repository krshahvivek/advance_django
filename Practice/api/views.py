import json
from django.http import JsonResponse
from yaml import serialize
from products.models import Product

# Create your views here.
def api_home(request, *args, **wrgs):
    body=request.body
    print(request.GET) #url query params
    data={}
    try:
        data=json.loads(body)
    except:
        pass
    # print(request.headers)
    # data['headers'] = request.headers #request.META
    data['params'] = dict(request.GET)
    data['content_type'] = request.content_type
    return JsonResponse(data)

def api_product(request):
    model_data = Product.objects.all().order_by("?").first()
    data={}
    if model_data:
        data['id'] = model_data.id
        data['title'] = model_data.title
        data['content'] = model_data.content
        data['price'] = model_data.price
    # return JsonResponse(data)

from django.forms.models import model_to_dict
#with serializers
def api_product_form(request):
    model_data = Product.objects.all().order_by("?").first()
    data={}
    if model_data:
        data = model_to_dict(model_data, fields=['id', 'title'])
    return JsonResponse(data)
    
    
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def api_rest(request):
    """
    DRF API views
    """
    # if request.method != "POST":
    #     return Response({"detail":"GET method is not allowed"}, status=405)
    model_data = Product.objects.all().order_by("?").first()
    data={}
    if model_data:
        data = model_to_dict(model_data, fields=['id', 'title'])
    return Response(data)

#django rest framework with model serializers

from products.serializers import ProductSerializer

@api_view(["GET"])
def api_rest_serializer(request):
    """
    DRF API views with serializers
    """
    instance = Product.objects.all().order_by("?").first()
    data={}
    if instance:
        data = ProductSerializer(instance).data
    return Response(data)

@api_view(['POST'])
def api_post_data(request):
    """
    DRF API views with serializers
    """
    serializer = ProductSerializer(data=request.data)
    # if serializer.is_valid():
    if serializer.is_valid(raise_exception=True): #this would make fiel mendatory to fill also will validate
        # instance = serializer.save()
        print(serializer.data)
        # data = serializer.data
        return Response(serializer.data)
    # return Response({"invalid":"not a good data"}, status=400) this fiel no longer require if we write line 79
