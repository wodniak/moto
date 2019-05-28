"""
    Input form for the user to pass motorcycle names
"""
from django import forms


class MotoInputForm(forms.Form):
    """
        Generic form
    """
    post = forms.CharField(max_length=200)
