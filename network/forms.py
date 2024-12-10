from django.forms import ModelForm, widgets
from django import forms

from .models import Post, User

# Forms for models.

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["content"]
        
        widgets = {
            "content": forms.Textarea(attrs={"class": "w3-input w3-border", "placeholder": "What's on your mind?", "rows": "5"})    
        }
        
class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ["following"]