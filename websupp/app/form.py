from django import forms

class CheckoutForm(forms.Form):
    address = forms.CharField(label="Địa chỉ nhận hàng", max_length=255)
    phone = forms.CharField(label="Số điện thoại", max_length=20)

from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'rating', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-3 py-2 rounded'}),
        }