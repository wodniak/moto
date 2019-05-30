"""
    Detail view of application
"""
import os
import json

from django.views.generic import TemplateView
from django.shortcuts import render
# from django.template import loader
from django.http import Http404
from django.http import HttpResponse

from PIL import Image

from ..forms import MotoInputTableLength
from ..models import CMotorcycles
from ..script.scraper import run


class DetailView(TemplateView):
    """
        Detail page
    """
    template_name = 'moto/detail.html'
    no_of_rows = 10  # default value

# ----------------------------------------------------
#   GET request
# ----------------------------------------------------

    def get(self, request):
        """
            Process GET request
        """
        form = MotoInputTableLength()
        motorcycles = CMotorcycles.objects.all()[:self.no_of_rows]
        context = {'form': form,
                   'CMotorcycles': motorcycles,
                   'no_of_rows': self.no_of_rows}
        return render(request, self.template_name, context)
# ----------------------------------------------------
# ----------------------------------------------------

# ----------------------------------------------------
#   POST request
# ----------------------------------------------------
    def post(self, request):
        """
            Process POST request
        """
        handler = request.POST.get('button')
        handler = getattr(
            self, handler, lambda: "Invalid button handler: {}".format(handler))
        return handler(request)

    def show_button(self, request):
        """
            Function handler to button clear_button
            Reset values in search list
        """
        form = MotoInputTableLength(request.POST)
        if form.is_valid():
            self.no_of_rows = form.cleaned_data['length']

        motorcycles = CMotorcycles.objects.all()[:self.no_of_rows]
        context = {'form': form,
                   'CMotorcycles': motorcycles,
                   'no_of_rows': self.no_of_rows}
        return render(request, self.template_name, context)
# ----------------------------------------------------
# ----------------------------------------------------

    def show_graphs(self, request):
        """
            Simply return a static image as a png
        """
        print('-----------------------dupa')
        dir_path = os.path.dirname(os.path.realpath(__file__))
        path_to_image = os.path.join(dir_path, "script/graph/barplot.png")
        Image.init()
        i = Image.open(path_to_image)

        response = HttpResponse(mimetype='image/png')
        i.save(response, 'PNG')
        return response
