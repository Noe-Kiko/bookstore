from core.models import Product, Category
from django import forms

class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title', 
            'image',
            'description',
            'price',
            'old_price',
            'condition',
            'stock_count',
            'publishDate',
            'category'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': "Book Title", "class":"form-control"}),
            'description': forms.Textarea(attrs={'placeholder': "Is it a specific edition? Talk about the book", "class":"form-control", "rows": 4}),
            'price': forms.NumberInput(attrs={'placeholder': "Selling Price", "class":"form-control"}),
            'old_price': forms.NumberInput(attrs={'placeholder': "Old Price", "class":"form-control"}),
            'condition': forms.TextInput(attrs={'placeholder': "Used or New", "class":"form-control"}),
            'stock_count': forms.NumberInput(attrs={'placeholder': "How many are in stock?", "class":"form-control"}),
            'publishDate': forms.TextInput(attrs={'placeholder': "e.g: May 20, 2025", "class":"form-control"}),
            'category': forms.Select(attrs={"class":"form-select"}),
        }