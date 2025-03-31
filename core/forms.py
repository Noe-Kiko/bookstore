from django import forms
from core.models import productReview

class productReviewForm(forms.ModelForm):
    reivew = forms.CharField(widget = forms.Textarea(attrs= {'placeholder': 'Write Review'}))

    class Meta:
        model = productReview
        fields = ['review', 'rating']