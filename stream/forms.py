
from django import forms
from django.contrib.auth.models import User

from stream.models import UserProfile, Comment, SubComment

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('picture','bio')

class CommentForm(forms.ModelForm):
    text = forms.TextInput()
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
    text = forms.TextInput()

    class Meta:
        model = SubComment
        fields = ('text',)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('text') == "":
            raise forms.ValidationError('Input Empty')
        return cleaned_data