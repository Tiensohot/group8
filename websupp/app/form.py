from django import forms

class CheckoutForm(forms.Form):
    address = forms.CharField(max_length=255, required=True)
    phone = forms.CharField(max_length=20, required=True)
    payment_method = forms.ChoiceField(
        choices=[
            ('cod', 'Thanh toán khi nhận hàng (COD)'),
            ('momo', 'Ví MoMo'),
            ('bank', 'Chuyển khoản ngân hàng'),
        ],
        widget=forms.RadioSelect,
        required=True
    )

from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'rating', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-3 py-2 rounded'}),
        }