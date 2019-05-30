"""
    Input form for the user to pass motorcycle names
"""
from django import forms
from .models import CMotorcycles


class MotoInputForm(forms.Form):
    """
        Generic form
    """
    post = forms.CharField(max_length=200)


class MotoInputTableLength(forms.Form):
    """
        Get input about length of table with parsed motorcycles to render
    """
    max_value = CMotorcycles.objects.count()
    length = forms.IntegerField(max_value=max_value, min_value=0)
