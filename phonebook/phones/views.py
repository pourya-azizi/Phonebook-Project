from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views import View, generic
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.views.generic import CreateView, ListView, UpdateView, TemplateView, DetailView
from django.views.generic.edit import FormMixin, FormView, BaseFormView
from . import forms, models
from .forms import EntryForm
from .models import Entry


@method_decorator(csrf_exempt, name='dispatch')
class CreateEntry(LoginRequiredMixin, CreateView):

    # def get_form_kwargs(self):
    #     kw = super(CreateEntry, self).get_form_kwargs()
    #     kw.update({'user': self.request.user})

    def post(self, request, *args, **kwargs):

        form_instance = forms.EntryForm(data=self.request.POST)
        request.session['phone_number'] = models.Entry.phone_number
        if form_instance.is_valid():
            form_instance.save(commit=False).user = self.request.user
            entry_object = form_instance.save()
            request.session['create entry'] = 'create entry'
            request.session.modified = True
            # print(dict(request.session))

            return JsonResponse(data={
                'success': True,
                'pk': entry_object.pk,
                'name': entry_object.name,
                'last_name': entry_object.last_name,
                'phone_number': entry_object.phone_number,
            }, status=201)
        else:
            request.session['error create entry'] = 'error create entry'
            request.session.modified = True
            return JsonResponse(data={
                'success': False,
            }, status=400)

    # def form_valid(self, form):
    #     form.instance.user = self.request.user
    #     f = super().form_valid(form)
    #     return JsonResponse({'status': 'True'}, status=201)
    #
    # def form_invalid(self, form):
    #     return JsonResponse({'status': 'False'}, status=400)


# @csrf_exempt
# @require_POST
# class create_entry(request):
#     """
#     Creates an entry via AJAX
#     """
#     form_instance = forms.EntryForm(data=request.POST)
#     if form_instance.is_valid():
#         entry_object = form_instance.save()
#         return JsonResponse(data={
#             'success': True,
#             'pk': entry_object.pk,
#             'name': entry_object.name,
#             'last_name': entry_object.last_name,
#             'phone_number': entry_object.phone_number
#         }, status=201)
#     else:
#         return JsonResponse(data={
#             'success': False,
#         }, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ShowAddEntryForm(FormView):
    """
    Show the add entry form page
    """
    form_class = forms.EntryForm
    template_name = 'phones/add_entry.html'


class ShowSearchForm(TemplateView):
    """
    Show the search form page
    """
    template_name = 'phones/search.html'


@method_decorator(login_required, name='dispatch')
class FindEntry(generic.View):
    """
    Finds a phonebook entry
    """

    def get(self, request, *args, **kwargs):

        phone_number = self.request.GET.get('phonenum', None)
        value = self.request.GET.get('value', None)
        request.session['search'] = 'search'
        request.session.modified = True
        if not phone_number:
            return JsonResponse({'success': False, 'error': 'No number specified.'}, status=400)

        if value == 'Contain':
            qs = Entry.objects.filter(phone_number__contains=phone_number)

        elif value == 'Exact':
            qs = Entry.objects.filter(phone_number__exact=phone_number, user=self.request.user)

        elif value == 'StartWith':
            qs = Entry.objects.filter(phone_number__startswith=phone_number, user=self.request.user)

        elif value == 'EndWith':
            qs = Entry.objects.filter(phone_number__endswith=phone_number, user=self.request.user)

        return JsonResponse(
            {
                'results': list(
                    qs.values()
                ),
                'count': qs.count()
            }
        )


@method_decorator(csrf_exempt, name='dispatch')
class ContactList(ListView):
    """
    Show the list of contacts
    """
    model = models.Entry
    paginate_by = 5
    template_name = 'phones/entry_list.html'

    def get_queryset(self):
        self.request.session['show list'] = 'show list'
        self.request.session.modified = True
        return Entry.objects.filter(user=self.request.user)


class ViewContact(DetailView):
    model = models.Entry


class EditContact(LoginRequiredMixin, UpdateView):
    model = models.Entry
    form = forms.EntryForm
    fields = (
        'name',
        'last_name',
        'phone_number',)
    template_name = 'phones/Entry_update_form.html'
    success_url = reverse_lazy('phones:contacts')

    # def post(self, request, *args, **kwargs):
    #
    #     form_instance = forms.EntryForm(data=self.request.POST)
    #     self.request.session['phone_number'] = models.Entry.phone_number
    #     if form_instance.is_valid():
    #         form_instance.save(commit=False).user = self.request.user
    #         entry_object = form_instance.save()
    #         request.session['create entry'] = 'create entry'
    #
    #         return JsonResponse(data={
    #             'success': True,
    #             'pk': entry_object.pk,
    #             'name': entry_object.name,
    #             'last_name': entry_object.last_name,
    #             'phone_number': entry_object.phone_number,
    #         }, status=201)
    #     else:
    #         request.session['error create entry'] = 'error create entry'
    #         return JsonResponse(data={
    #             'success': False,
    #         }, status=400)

    # def __getattr__(self, item):
    #     self.request.session['action'] = {}


class SessionView(View):
    template_name = 'phones/phone_activate.html'

    def get(self, request, *args, **kwargs):
        i = 0
        s = dict(request.session)
        # for key, value in dict(request.session).items():
        #     print(key, value)
        #     if i > 2:
        #         s[key] = value
        #         i += 1
        context = {
            'session': s
        }
        print(s)
        return render(request, self.template_name, context=context)
