from django.db import models

# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=120)
    content = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=99.99)

    # after django rest framework with model serializers work
    @property
    def sale_price(self):
        return "%.2f" %(float(self.price) * 0.8)

    def get_discount(self):
        return "103"

"""
class Author(models.Model):
    id = models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    email=models.EmailField(max_length=100)
class CoverImage(models.Model):
    url=models.URLField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)

class Tags(models.Model):
    name=models.CharField(max_length=20)


class Blog(models.Model):
    class BLOG_STATUS(models.TextChoices):
        PUBLISH = 'PUBLISH', _('PUBLISH')
        DRAFT = 'DRAFT', _('DRAFT')
        REVIEW = 'REVIEW', _('REVIEW') 

    author=models.ForeignKey(Author, on_delete=models.PROTECT) # on delete protect from deleteting if any relation with another table, and on_delete=models.CASCADE with delete whole date which is makes relations with other table  
    tag=models.ManyToManyField(Tags, on_delete=models.PROTECT)
    coverimage=models.OneToOneField(CoverImage, on_delete=models.PROTECT)
    title=models.CharField(max_length=100)
    content=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    status= models.CharField(choices=BLOG_STATUS.choices, max_length=20)
    def __str__(self):
        return self.author  

#in setting part

TokenAuthentication

"""