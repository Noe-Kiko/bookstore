from core.models import Product
from django import forms

class AddProductForm(forms.ModelForm):
    class Meta:
        title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Book Title", "class":"form-control"}))
        description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': "Is it a specific edition? Talk about the book", "class":"form-control"}))
        price = forms.CharField(widget=forms.NumberInput(attrs={'placeholder': "Selling Price", "class":"form-control"}))
        old_price = forms.CharField(widget=forms.NumberInput(attrs={'placeholder': "Old Price", "class":"form-control"}))
        condition = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Used or New", "class":"form-control"}))
        stock_count = forms.CharField(widget=forms.NumberInput(attrs={'placeholder': "How many are in stock?", "class":"form-control"}))
        publishDate = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'placeholder': "e.g: 05-20-25", "class":"form-control"}))
        tags = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Tags", "class":"form-control"}))
        image = forms.ImageField(widget=forms.FileInput(attrs={"class":"form-control"}))

        # Grabbing objects from Product table inside of 
        model = Product
        fields = {
            'title', 
            'image',
            'description',
            'price',
            'old_price',
            'condition',
            'stock_count',
            'publishDate',
            'category'
        }

        widgets = {
        # 'mdf': DateTimePickerInput
    }