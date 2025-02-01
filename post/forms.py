from django import forms
from post.models import Post


class NewPostform(forms.ModelForm):
    # content = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=True)
    
    picture = forms.ImageField(required=True)
    caption = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Caption'}), required=True)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Tags | Seperate with comma'}))

    class Meta:
        model = Post
        fields = ['picture', 'caption', 'tags']
    
    def clean_body(self):
        caption = self.cleaned_data.get('caption')
        if len(caption) > 3000:
            raise forms.ValidationError("Caption text cannot exceed 3000 characters.")
        return caption