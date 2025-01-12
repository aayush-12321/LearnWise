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

# from django.core.exceptions import ValidationError

# class NewPostform(forms.ModelForm):
#     picture = forms.ImageField(required=False)
#     caption = forms.CharField(
#         widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Caption'}),
#         required=False
#     )
#     tags = forms.CharField(
#         widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Tags | Separate with comma'}),
#         required=False
#     )

#     class Meta:
#         model = Post
#         fields = ['picture', 'caption', 'tags']

#     def clean(self):
#         cleaned_data = super().clean()
#         picture = cleaned_data.get('picture')
#         caption = cleaned_data.get('caption')
#         tags = cleaned_data.get('tags')

#         # Validation to ensure tags cannot be submitted alone
#         if not (picture or caption) and tags:
#             raise ValidationError(
#                 "Tags cannot be submitted alone. Please include either a picture, a caption, or both."
#             )

#         if not (picture or caption or tags):
#             raise ValidationError(
#                 "At least one of 'Picture', 'Caption', or 'Tags' must be provided."
#             )

#         return cleaned_data
