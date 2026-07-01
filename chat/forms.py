from django import forms
from .models import Message

class Message_form(forms.ModelForm):
    class Meta :
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'placeholder': 'Type your message...',
                'class': 'form-control'
            })
        }