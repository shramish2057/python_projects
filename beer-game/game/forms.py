from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import *


class ExtendedUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=150)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit: 
            user.save()
        return user



class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['is_instructor']



class GameCreationForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = '__all__'
        exclude = ('admin','roles','active', 'info_sharing', 'rounds_completed', 'is_completed')

        widgets ={
            'nr_rounds': forms.NumberInput(attrs={'class':'form-control'}),
            'info_delay': forms.NumberInput(attrs={'class':'form-control'}),
            'holding_cost': forms.NumberInput(attrs={'class':'form-control'}),
            'backlog_cost': forms.NumberInput(attrs={'class':'form-control'}),
            'starting_inventory': forms.NumberInput(attrs={'class':'form-control'}),

            'distributor_present': forms.CheckboxInput(attrs={'class':'form-check-input', 'onclick':'check_distributor()'}),
            'wholesaler_present': forms.CheckboxInput(attrs={'class':'form-check-input', 'onclick':'check_wholesaler()'}),
        }
    


# created a custom form instead of using a model form
# because the model needs some role models which don't
# exist at first, that's why most of the data will be taken
# from the same as the Game model itself
class ExtendedGameCreationForm(forms.Form):
    retailer = forms.ModelChoiceField(queryset=User.objects.all().filter(userprofile__is_instructor=False), required=True, widget=forms.Select(attrs={'class':'form-select'}))
    wholesaler = forms.ModelChoiceField(queryset=User.objects.all().filter(userprofile__is_instructor=False), required = False, widget=forms.Select(attrs={'class':'form-select'}))
    distributor = forms.ModelChoiceField(queryset=User.objects.all().filter(userprofile__is_instructor=False), required = False, widget=forms.Select(attrs={'class':'form-select'}))
    factory = forms.ModelChoiceField(queryset=User.objects.all().filter(userprofile__is_instructor=False), required= True, widget=forms.Select(attrs={'class':'form-select'}))


class GameUpdateForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = '__all__'
        exclude = ('admin','roles','active', 'info_sharing', 'is_completed', 'starting_inventory', 'rounds_completed')

        widgets ={
            'nr_rounds': forms.NumberInput(attrs={'class':'form-control'}),
            'info_delay': forms.NumberInput(attrs={'class':'form-control'}),
            'holding_cost': forms.NumberInput(attrs={'class':'form-control'}),
            'backlog_cost': forms.NumberInput(attrs={'class':'form-control'}),

            'is_active': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'distributor_present': forms.CheckboxInput(attrs={'class':'form-check-input', 'onclick':'check_distributor()'}),
            'wholesaler_present': forms.CheckboxInput(attrs={'class':'form-check-input', 'onclick':'check_wholesaler()'}),
        }


class ExtendedGameUpdateForm(forms.Form):
    retailer = forms.ModelChoiceField(queryset=User.objects.all().filter(userprofile__is_instructor=False), required=True, widget=forms.Select(attrs={'class':'form-select'}))
    wholesaler = forms.ModelChoiceField(queryset=User.objects.all().filter(userprofile__is_instructor=False), required = False, widget=forms.Select(attrs={'class':'form-select'}))
    distributor = forms.ModelChoiceField(queryset=User.objects.all().filter(userprofile__is_instructor=False), required = False, widget=forms.Select(attrs={'class':'form-select'}))
    factory = forms.ModelChoiceField(queryset=User.objects.all().filter(userprofile__is_instructor=False), required= True, widget=forms.Select(attrs={'class':'form-select'}))