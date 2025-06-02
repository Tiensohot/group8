from django import forms

class CheckoutForm(forms.Form):
    address = forms.CharField(label="Địa chỉ nhận hàng", max_length=255)
    phone = forms.CharField(label="Số điện thoại", max_length=20)
