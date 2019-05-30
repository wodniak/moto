"""
    Declared views of application
"""
import os
import json

from django.views.generic import TemplateView
from django.shortcuts import render
from django.shortcuts import redirect
# from django.template import loader
from django.http import Http404
from django.http import HttpResponse
from PIL import Image

from ..forms import MotoInputForm
from ..models import CMotorcycles
from ..script.scraper import run


class MotoView(TemplateView):
    """
    main page
    """
    template_name = 'moto/index.html'
    next_template_name = 'moto/detail.html'
    moto_to_scrap = []

# ----------------------------------------------------
#   GET request
# ----------------------------------------------------

    def get(self, request):
        """
            Process GET request
        """
        form = MotoInputForm()
        context = {'form': form,
                   'moto_to_scrap': self.moto_to_scrap}
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

    def clear_button(self, request):
        """
            Function handler to button clear_button
            Reset values in search list
        """
        form = MotoInputForm()
        self.moto_to_scrap.clear()
        context = {'form': form,
                   'moto_to_scrap': self.moto_to_scrap}
        return render(request, self.template_name, context)

    def add_button(self, request):
        """
            Function handler to button add_button
            Invoked when clicked
        """
        form = MotoInputForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['post']
            if text not in self.moto_to_scrap:
                self.moto_to_scrap.append(text)

        context = {'form': form,
                   'moto_to_scrap': self.moto_to_scrap}

        return render(request, self.template_name, context)

    def submit_button(self, request):
        """
            Function handler to button add_button
            Start scraper.py script
        """
        dir_path = os.path.dirname(os.path.realpath(__file__))
        path_to_file = os.path.join(dir_path, "../script/config.json")

        # create config.json
        json_dict = {"vehicle": []}
        for name in self.moto_to_scrap:
            if len(name.split()) == 2:
                brand, model = name.split()

                json_dict['vehicle'].append({"brand": brand,
                                             "model": model})
            else:
                json_dict['vehicle'].append({"brand": name})

        with open(path_to_file, 'w') as config_file:
            json.dump(json_dict, config_file, indent=4, sort_keys=True)

        # execute script
        moto_data_base = run()

        # create table in database and send some to html
        moto_data_base.to_sql()
        return redirect('detail')
