"""
    Declared views of application
"""

from django.views.generic import TemplateView
from django.shortcuts import render
from django.template import loader
from django.http import Http404

from .forms import MotoInputForm
from .models import CMotorcycles

class MotoView(TemplateView):
    """
    main page
    """
    template_name = 'moto/index.html'
    moto_to_scrap = []

    def get(self, request):
        """
            Process GET
        """
        form = MotoInputForm()
        # self.latest_moto_list = CMotorcycles.objects.all().order_by('-pub_date')

        context = {'form' : form,
                   'moto_to_scrap': self.moto_to_scrap}
        return render(request, self.template_name, context)


    def post(self, request):
        """
            Process POST
        """
        form = MotoInputForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['post']
            if text not in self.moto_to_scrap:
                self.moto_to_scrap.append(text)
                
        context = {'form' : form,
                   'moto_to_scrap' : self.moto_to_scrap}

        return render(request, self.template_name, context)

# def index(request):
#     """
#         main page
#     """
#     latest_moto_list = CMotorcycles.objects.all().order_by('-pub_date')
#     template = loader.get_template('moto/index.html')
#     context = {
#         'latest_moto_list': latest_moto_list,
#     }
#     return HttpResponse(template.render(context, request))


def detail_moto(request, idx):
    """
        show detailed info about motorycycle
    """
    try:
        detail = CMotorcycles.objects.get(pk=idx)
        print(detail)
    except CMotorcycles.DoesNotExist:
        raise Http404("Moto with ID {} does not exist".format(idx))
    return render(request, 'moto/detail.html', {'detail': detail})
    # return HttpResponse("Detailed information on moto ID {}".format(idx))
