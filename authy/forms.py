from django import forms
from authy.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm



# class EditProfileForm(forms.ModelForm):
#     image = forms.ImageField(required=True)
#     first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'First Name'}), required=True)
#     last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Last Name'}), required=True)
#     bio = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Bio'}), required=True)
#     url = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'URL'}), required=True)
#     location = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Address'}), required=True)

#     class Meta:
#         model = Profile
#         fields = ['image', 'first_name', 'last_name', 'bio', 'url', 'location']

class EditProfileForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "First Name"}),
        required=False,
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Last Name"}),
        required=False,
    )
    bio = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Bio"}),
        required=False,
    )
    url = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "URL"}),
        required=False,
    )
    location = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Address"}),
        required=False,
    )
    skills = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter your skills (e.g., Python, Data Analysis)'}),required=False, max_length=200)
    interests = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter your interests (e.g., Web Development, Machine Learning)'}),required=False, max_length=200)
    

    class Meta:
        model = Profile
        fields = ["image", "first_name", "last_name", "bio", "url", "location",'role', 'skills', 'interests']





# class UserRegisterForm(UserCreationForm):
#     username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'prompt srch_explore'}), max_length=50, required=True)
#     # username = forms.EmailInput(widget=forms.TextInput(attrs={'placeholder': 'Username'}), max_length=50, required=True)

#     email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email', 'class': 'prompt srch_explore'}))
#     password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password', 'class': 'prompt srch_explore'}))
#     password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'prompt srch_explore'}))
#     # email = forms.EmailField()

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']



# class UserRegisterForm(UserCreationForm):
#     username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'prompt srch_explore'}), max_length=50, required=True)
#     email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'prompt srch_explore'}))
#     password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password', 'class': 'prompt srch_explore'}))
#     password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'prompt srch_explore'}))
    
#     # New fields
#     first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}), required=False, max_length=30)
#     last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}), required=False, max_length=30)
#     bio = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Tell us about yourself'}), required=False)
#     location = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Location'}), required=False, max_length=100)
#     url = forms.URLField(widget=forms.TextInput(attrs={'placeholder': 'Website URL'}), required=False)
#     image = forms.ImageField(required=False)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'bio', 'location', 'url', 'image']






class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'prompt srch_explore'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}), required=False, max_length=200)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}), required=False, max_length=200)
    bio = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Tell us about yourself'}), required=False)
    location = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Location'}), required=False, max_length=200)
    url = forms.URLField(widget=forms.TextInput(attrs={'placeholder': 'Website URL'}), required=False)
    image = forms.ImageField(required=False)

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
        profile.location = self.cleaned_data.get('location')
        profile.url = self.cleaned_data.get('url')
        
        # Set the profile image if provided
        if self.cleaned_data.get('image'):
            profile.image = self.cleaned_data.get('image')
        
        if commit:
            user.save()
            profile.save()
        
        return user

##########

class ProfileForm(forms.ModelForm):
    skills = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter your skills (e.g., Python, Data Analysis)'}),required=False, max_length=200)
    interests = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter your interests (e.g., Web Development, Machine Learning)'}),required=False, max_length=200)
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,  # Use the choices defined in the Profile model
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    class Meta:
        model = Profile
        fields = ['role', 'skills', 'interests'] 

#########
