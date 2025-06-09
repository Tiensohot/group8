from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    error_messages = {
        'password_mismatch': "Mật khẩu xác nhận không khớp.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = 'Tên đăng nhập'
        self.fields['password1'].label = 'Mật khẩu'
        self.fields['password2'].label = 'Xác nhận mật khẩu'

        self.fields['username'].widget.attrs.update({
            'placeholder': ''
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': ''
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': ''
        })

        self.fields['username'].error_messages.update({
            'required': 'Bạn phải nhập tên đăng nhập.',
            'unique': 'Tên đăng nhập đã được sử dụng.',
        })

        self.fields['password1'].error_messages.update({
            'required': 'Bạn phải nhập mật khẩu.',
            'min_length': 'Mật khẩu phải có ít nhất 8 ký tự.',
        })

        self.fields['password2'].error_messages.update({
            'required': 'Bạn phải xác nhận lại mật khẩu.',
        })

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
