
from django import forms
from django.contrib.auth.models import User

from stream.models import UserProfile, Comment, SubComment

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Make it safe!!',
                                                        'class': 'form-password'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'What will you be called?',
                                                        'class': 'form-username'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'example@email.com',
                                                        'class': 'form-email'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password')



class UserProfileForm(forms.ModelForm):
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': 'Tell us about you!',
                                                       'class': 'form-bio',
                                                       'rows': 3,
                                                       'cols': 40,
                                                       'style': 'height: 3em;'
                                                       }))

    class Meta:
        model = UserProfile
        fields = ('picture','bio')

class CommentForm(forms.ModelForm):
    text = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-bio',
                                                       'rows': 20,
                                                       'cols': 100,
                                                       'style': 'height: 5em;'
                                                       }))
    rating = forms.IntegerField(required=True,
                                initial=0,
                                help_text="Rating between 1-5")

    class Meta:
        model = Comment
        fields = ('text', 'rating',)
        exclude = ('streamer', 'user_name',)

    def clean(self):
        cleaned_data = super().clean()
        if not 1 <= cleaned_data.get('rating') <= 5:
            raise forms.ValidationError('Rating between 1 and 5')
        return cleaned_data


class SubCommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'What do you have to say?',
                                                       'class': 'form-bio',
                                                       'rows': 20,
                                                       'cols': 100,
                                                       'style': 'height: 5em;'
                                                       }))

    class Meta:
        model = SubComment
        fields = ('text',)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('text') == "":
            raise forms.ValidationError('Input Empty')
        return cleaned_data