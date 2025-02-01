from django.contrib.auth.models import User
from comment.models import Comment
from django import forms

class NewCommentForm(forms.ModelForm):
    body = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Write comment'}), required=True)
    
    class Meta:
        model = Comment
        fields = ("body",)
    
    def clean_body(self):
        body = self.cleaned_data.get('body')
        if len(body) > 2000:
            raise forms.ValidationError("Body text cannot exceed 2000 characters.")
        return body