from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, ListView, DetailView
from django.utils.translation import gettext_lazy as _, ngettext
from .models import Profile
from .forms import MyUserCreationForm, ProfileCreateForm
from random import random
from django.views.decorators.cache import cache_page


class HelloView(View):
    welcome_message = _('welcome hello world')

    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get('items') or 0
        items = int(items_str)
        products_line = ngettext(
            'one product',
            '{count} product',
            items
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f'<h1>{self.welcome_message}</h1>'
            f'<h2>{products_line}</h2>'
        )


class AboutMeView(TemplateView):
    template_name = 'myauth/about-me.html'


class RegisterView(CreateView):
    form_class = MyUserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:about-me')

    def form_valid(self, form):
        response = super().form_valid(form)
        profile = Profile.objects.create(user=self.object)

        if form.cleaned_data.get('avatar'):
            profile.avatar = form.cleaned_data['avatar']
            profile.save()

        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(
            self.request,
            username=username,
            password=password
        )
        login(self.request, user)
        return response


class CreateProfileView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'myauth:login'
    template_name = 'myauth/create_profile.html'

    def test_func(self):
        user_id = self.kwargs.get('user_id')
        return (self.request.user.is_staff
                or
                self.request.user.id == int(user_id))

    def get(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, pk=user_id)
        profile, created = Profile.objects.get_or_create(user=user)

        form = ProfileCreateForm(instance=profile)

        context = {
            'form': form,
            'user': user,
        }
        return render(request, self.template_name, context=context)

    def post(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, pk=user_id)
        profile, created = Profile.objects.get_or_create(user=user)

        form = ProfileCreateForm(
            request.POST, request.FILES, instance=profile
        )

        if form.is_valid():
            form.save()
            return redirect('myauth:user-details', pk=user.id)

        context = {
            'form': form,
            'user': user,
        }
        return render(request, self.template_name, context=context)


class UserDetailView(DetailView):
    model = User
    template_name = 'myauth/user_detail.html'


class MyLogoutView(LogoutView):
    next_page = reverse_lazy('myauth:login')


class UserListView(ListView):
    model = User
    template_name = 'myauth/user_list.html'


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    # В случае использования здесь этого декоратора необходимо
    # делать проверку наличия доступа, чтобы избежать
    # бесконечного зацикливания, так как нет специального флага,
    # как во view, основанном на классе.
    response = HttpResponse('Cookie set')
    response.set_cookie('fizz', 'buzz', max_age=3600)
    return response


@cache_page(60 * 2)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get('fizz', 'default value')
    return HttpResponse(f'Cookie value: {value!r} + {random()}')


@permission_required('myauth.view_profile', raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session['sesval'] = 'value'
    return HttpResponse('Session set!')


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get('sesval', 'default value')
    return HttpResponse(f'Session value: {value!r}')


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({'foo': 'bar', 'spam': 'eggs'})
