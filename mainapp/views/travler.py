from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# from mainapp.forms.travler import TravlerLoginForm
# from mainapp.forms.travler import TravlerCreateForm, TravlerUpdateForm
from mainapp.models import Travler


# def login_view(request):
#     if request.method == 'POST':
#         form = TravlerLoginForm(data=request.POST)
#         if form.is_valid():
#             username = request.POST['username']
#             password = request.POST['password']
#             user = auth.authenticate(username=username, password=password)
#             if user and user.is_active:
#                 auth.login(request, user)
#                 return redirect(reverse('mainapp:root'))
#     else:
#         form = TravlerLoginForm()
#     context = {
#         'form': form,
#     }
#     return render(request, 'mainapp/travler/login.html', context)
#
#
# def logout_view(request):
#     auth.logout(request)
#     return redirect(reverse('mainapp:root'))
#
#
# def create_travler_view(request):
#     title = 'Книгошар - Регистрация'
#
#     if request.method == 'POST':
#         form = TravlerCreateForm(request.POST, request.FILES)
#
#         if form.is_valid():
#             form.save()
#             return redirect(reverse('travler:login'))
#     else:
#         form = TravlerCreateForm()
#     context = {
#         'title': title,
#         'form': form,
#     }
#     return render(request, 'authapp/travler/create.html', context)
#
#
# def update_travler_view(request, username):
#     title = 'Книгошар - Настройки'
#     if request.method == 'POST':
#         form = TravlerUpdateForm(request.POST, request.FILES)
#
#         if form.is_valid():
#             form.save()
#             return redirect(reverse('travler:update'))
#     else:
#         form = TravlerUpdateForm()
#     context = {
#         'title': title,
#         'form': form,
#     }
#     return render(request, 'authapp/travler/update.html', context)


class RestTravlerCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Travler

    def test_func(self):
        return self.request.user.is_superuser


class RestTravlerListView(ListView):
    model = Travler

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RestTravlerListView, self).get_context_data(**kwargs)

        username = self.request.GET.get('user', 'travl')
        try:
            user = Travler.objects.get(username=username)
        except ObjectDoesNotExist:
            return {
                'status': 404,
                'description': 'User does not exist',
                'context': {'username': username},
            }

        data = {
            'status': 200,
            'user': user.username
        }
        users = context.get('travler_list')
        print(context)
        data['users'] = [_.serialize(username, detailed=False) for _ in users.all()]
        data['count'] = len(data['users'])

        return data

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class RestTravlerDetailView(DetailView):
    model = Travler
    # query_pk_or_slug = True
    slug_url_kwarg = 'username'

    # def get_queryset(self):
    #     return Travler.objects.filter(username=self.kwargs['username'])

    def get_object(self, queryset=None):
        try:
            return Travler.objects.get(username=self.kwargs['username'])
        except ObjectDoesNotExist:
            raise Http404

    def get_context_data(self, *, object_list=None, **kwargs):
        username = self.request.GET.get('user', 'travl')
        travler_name = self.kwargs.get('username')
        try:
            user = Travler.objects.get(username=username)
        except ObjectDoesNotExist:
            return {
                'status': 404,
                'description': 'User does not exist',
                'context': {'username': username},
            }

        data = {
            'status': 200,
            'user': user.username
        }
        travler = Travler.objects.get(username=travler_name)
        data['userdata'] = travler.serialize(username)

        return data

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class RestTravlerUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Travler

    def test_func(self):
        return self.request.user.is_superuser


class RestTravlerDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Travler

    def test_func(self):
        return self.request.user.is_superuser
