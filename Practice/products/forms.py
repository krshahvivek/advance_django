from django import forms

from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        field = [
            'title',
            'content',
            'price'
        ]