from rest_framework import generics

from .models import Product
from .serializers import ProductSerializer

class ProductCreateAPIView(generics.CreateAPIView):
    queryset=Product.objects.all()
    serializer_class = ProductSerializer
#while creating a data we want to assign some thing
    def perform_create(self, serializer):
        print(serializer.validated_data)
        title = serializer.validated_data.get('title')
        content = serializer.validated_data.get('content')
        if content is None:
            content = title
        serializer.save(content=content)
        #send django signals - if its not necessarily related directly to the model itself
product_create_view = ProductCreateAPIView.as_view()

class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset=Product.objects.all()
    serializer_class = ProductSerializer

product_detail_view = ProductDetailAPIView.as_view()

class ProductUpdateAPIView(generics.UpdateAPIView):
    queryset=Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'

    def perform_update(self, serializer):
        instance = serializer.save()
        if not instance.content:
            instance.content = instance.title

product_update_view = ProductUpdateAPIView.as_view()




class ProductDestroyAPIView(generics.DestroyAPIView):
    queryset=Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'

    def perform_destroy (self, instance):
        super().perform_delete(instance)

product_destroy_view = ProductDestroyAPIView.as_view()
#function based views crud application

from rest_framework.decorators import api_view
from rest_framework.response import Response

# from django.http import Http404
from django.shortcuts import get_list_or_404
@api_view(['GET', 'POST']) 
def product_alt_view(request, pk=None, *args, **kwargs):
        method = request.method

        if method == "GET":
            # pass
            #url_args ??
            if pk is not None:
                #get request -> detail view
                # queryset=Product.objects.filter(pk=pk)
                # if not queryset.exist():
                    # raise Http404 
                    # (or we could do )
                obj = get_list_or_404(Product, pk=pk)
                data = ProductSerializer(obj, many=False).data
                return Response(data)
            # else:
            #list_view
            queryset=Product.objects.all()
            data = ProductSerializer(queryset, many=True).data
            return Response(data)

        if method == "POST":
            # create an item
            serializer = ProductSerializer(data=request.data)
            # if serializer.is_valid():
            if serializer.is_valid(raise_exception=True):
                title = serializer.validated_data.get('title')
                content = serializer.validated_data.get('content')
                if content is None:
                    content = title
                serializer.save(content=content)
                # instance = serializer.save()
                # print(serializer.data)
                # data = serializer.data
                return Response(serializer.data)
            #return Response({"invalid":"not a good data"}, status=400) this fiel no longer require if we write line 79



#Mixins and a Generic API views
from rest_framework import mixins
class ProductMixinView(
    mixins.ListModelMixin,
    generics.GenericAPIView
    ):

    queryset=Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    # def post(): 
product_mixin_view = ProductMixinView.as_view()