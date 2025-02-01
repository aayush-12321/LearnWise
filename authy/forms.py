from django import forms
from authy.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Rating

class EditProfileForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "First Name"}),
        required=False,
        max_length=200,
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Last Name"}),
        required=False,
        max_length=200,
    )
    bio = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Bio"}),
        required=False,
        max_length=800,
    )
    url = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "URL"}),
        required=False,
        max_length=200,
    )
    location = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Address"}),
        max_length=300,
        required=False,
    )
    skills = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter your skills (e.g., Python, Data Analysis)'}),required=False, max_length=800)
    interests = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter your interests (e.g., Web Development, Machine Learning)'}),required=False, max_length=800)
    

    class Meta:
        model = Profile
        fields = ["image", "first_name", "last_name", "bio", "url", "location",'role', 'skills', 'interests']

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'prompt srch_explore'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}), required=False, max_length=200)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}), required=False, max_length=200)
    bio = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Tell us about yourself'}), required=False, max_length=800)
    # location = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Location'}), required=False, max_length=200)
    location = forms.CharField(widget=forms.HiddenInput(), required=False, max_length=300)
    manual_location = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Type your address'}), required=False, max_length=300)
    url = forms.URLField(widget=forms.TextInput(attrs={'placeholder': 'Website URL'}), required=False, max_length=200)
    image = forms.ImageField(required=False)

    skills = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter your skills (e.g., Python, Data Analysis)'}),required=False, max_length=500)
    interests = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter your interests (e.g., Web Development, Machine Learning)'}),required=False, max_length=500)
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,  # Use the choices defined in the Profile model
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        # Save the user instance
        user = super().save(commit=commit)
        
        # Create or update the Profile instance
        profile, created = Profile.objects.get_or_create(user=user)
        
        # Set the profile fields
        profile.first_name = self.cleaned_data.get('first_name')
        profile.last_name = self.cleaned_data.get('last_name')
        profile.bio = self.cleaned_data.get('bio')
        # profile.location = self.cleaned_data.get('location')
        profile.url = self.cleaned_data.get('url')
        profile.skills = self.cleaned_data.get('skills')
        profile.interests = self.cleaned_data.get('interests')
        profile.role = self.cleaned_data.get('role')
        
        # Set the profile image if provided
        if self.cleaned_data.get('image'):
            profile.image = self.cleaned_data.get('image')

        
        # Use manual location if provided, otherwise use map location
        manual_location = self.cleaned_data.get('manual_location')
        if manual_location:
            profile.location = manual_location
        else:
            profile.location = self.cleaned_data.get('location')
        
        if commit:
            user.save()
            profile.save()
        
        return user

class RatingForm(forms.ModelForm):
    MAX_REVIEW_LENGTH = 300  

    class Meta:
        model = Rating
        fields = ['review', 'rating', 'rate_type']
        widgets = {
            'review': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your review here...','class': 'review-textarea'}),
        }

    def clean_review(self):
        review = self.cleaned_data.get('review')
        if review and len(review) > self.MAX_REVIEW_LENGTH:
            raise forms.ValidationError(f"Review cannot exceed {self.MAX_REVIEW_LENGTH} characters.")
        return review
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not rating:  # Check if rating is None or empty
            raise forms.ValidationError("Please select a rating.")
        return rating


