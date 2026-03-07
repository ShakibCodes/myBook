from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Folder, File


class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'maxlength': 300}),
        }


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'visibility', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file']

    def save(self, folder, commit=True):
        instance = super().save(commit=False)
        instance.folder = folder
        instance.name = instance.file.name.split('/')[-1]
        instance.file_size = instance.file.size
        instance.mime_type = getattr(instance.file.file, 'content_type', '')
        if commit:
            instance.save()
        return instance
