from requests import request
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
        content = serializer.validated_data.get('content') or None
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
                content = serializer.validated_data.get('content') or None
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
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    generics.GenericAPIView
    ):

    queryset=Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'

    def get(self, request, pk=None, *args, **kwargs):
        print(args, kwargs)
        pk = kwargs.get("pk")
        if pk is not None:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
    
    def perform_update(self, serializer):
        title = serializer.validated_data.get('title')
        content = serializer.validated_data.get('content') or None
        if content is None:
            content = "this is a single view doing cool stuff"
        serializer.save(content=content)
product_mixin_view = ProductMixinView.as_view()



#permission and Generic views 
from rest_framework import permissions, authentication
from .permissions import IsStaffEditorPermission
class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [permissions.IsAuthenticated]    
    authentication_classes = [authentication.SessionAuthentication]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # permission_classes = [permissions.DjangoModelPermissions]
    permission_classes = [IsStaffEditorPermission]

    def perform_update(self, serializer):
        title = serializer.validated_data.get('title')
        content = serializer.validated_data.get('content') or None
        if content is None:
            content = "this is a single view doing cool stuff"
        serializer.save(content=content)
product_list_create_mixin_view = ProductListCreateAPIView.as_view()

#class based views
from rest_framework.views import APIView
class createbog(APIView):
    def get(self, request):
        pro=Product.objects.all()
        response=ProductSerializer(pro, many=True)
        return Response(response.data)

    def post(self, request, product_id):
        pro_data=request.data
        '''
        # this is token part
        user_req = request.user
        author = models.Author.objects.get(user=user_req)
        pro_data['author'] = author.id
        #though we were giving author name mannualy but not after token part 
        '''
        pro_data['id'] = product_id
        pro_serializer=ProductSerializer(data=pro_data)
        if pro_serializer.is_valid():
            pro_serializer.save()
            return Response({'msg':'saved'},{'data':pro_serializer.data})
        else:
            return Response({'msg': pro_serializer.errors})
# while post data we might get some error, so we would put some serializers extra_field.
"""
class ProSerializer():
    blog=BlogSerializer(source='field which is from model ', many=False)
    author_id=serializers.IntegersField()

    def create(self, validate_data):
        print(validate_data)
        return super().create(validated_data)

    class meta:
        extra_kwargs = {'author_id':{'write_only':True}} #this part would not let show to user
"""

from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny 
class Loginapi(APIView):
    # for permission
    permission_classes = [AllowAny]
    def post(self, request):    
        req_data=request.data
        user_req=User.objects.get(username=req_data['username'])
        if user.check_password(req_data['password']):
            print('correct password')
            print(req_data)
            token, create = Token.objects.get_or_create(user=user_req)
            return Response(data={'token':token.key})
        print('wrong password')
        return Response(data={'data': 'bad password'})

class Signup(APIView):
    permission_classes=[AllowAny]

    def post(self, respect):
        request_data=request.data
        new_product=Product.objects.create_user(
            product_name=request_data['name']   
        )
        token, create = Token.objects.get_or_create(product=new_product)
        return Response(data={'token': token.key})