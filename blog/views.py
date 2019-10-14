from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import resolve
from django.conf import settings
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth.views import LoginView
from django.views.generic import ListView
from django.views.generic.edit import FormView, DeleteView
from .models import Post, User
from .forms import PostForm
from django.views.generic.edit import UpdateView
from .tasks import send_email, publication_delay, new_comment_email_send
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from .tokens import token_generator


def main(request):
    pathname = 'login' if not request.user.is_authenticated else settings.LOGIN_REDIRECT_URL
    return redirect(pathname)


def get_recipient_list(mode='login_fail'):
    _filter = Q(login_fail_notification=True) if mode == 'login_fail' else Q(sign_up_notification=True)
    return [user.email for user in User.objects.filter(_filter, is_superuser=True)]


class CustomLoginView(LoginView):
    def form_valid(self, form):
        super().form_valid(form)
        obj = form.get_user()
        if obj.is_staff or obj.is_superuser:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return HttpResponseRedirect('/')

    def form_invalid(self, form):
        invalid = form.errors.get('__all__', None)

        if invalid:
            recipient_list = get_recipient_list()
            send_email.delay(form.cleaned_data, recipient_list)
        return self.render_to_response(self.get_context_data(form=form))


def logout_view(request):
    is_superuser = request.user.is_superuser
    is_staff = request.user.is_staff
    auth_logout(request)

    if is_staff or is_superuser:
        return redirect('login')
    else:
        return redirect('ui_posts_list')


def sign_up(request):
    form = SignUpForm(request.POST) if request.method == 'POST' else SignUpForm()

    if form.is_valid():
        form.save()
        email = form.cleaned_data.get('email')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=email, password=raw_password)
        login(request, user)
        recipient_list = get_recipient_list()
        send_email.delay(form.cleaned_data, recipient_list, mode='sign_up')
        return redirect('ui_posts_list')

    context = {
        'form': form,
        'email': request.POST.get('email', ''),
        'password1': request.POST.get('password1', ''),
        'first_name': request.POST.get('first_name', ''),
        'last_name': request.POST.get('last_name', ''),
        'age': request.POST.get('age', ''),
    }
    return render(request, 'registration/register.html', context)


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'post/list.html'
    paginate_by = 10


class PostFormView(LoginRequiredMixin, FormView):
    template_name = 'post/form.html'
    form_class = PostForm
    success_url = 'posts-list'

    def post(self, request, *args, **kwargs):
        instance = None
        data = request.POST
        if 'slug' in data and 'pk' in data:
            instance = get_object_or_404(Post, slug=data['slug'], id=data['pk'])

        form = self.get_form() if instance is None else self.form_class(
            data, self.request.FILES, instance=instance)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, instance=None):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        try:
            obj.save()

            if obj.delay:
                print('HERE')
                publication_delay.apply_async(args=[obj.id], eta=obj.delay_time, task_id=f'publication_delay_{obj.id}')
            return HttpResponseRedirect(self.get_success_url())
        except IntegrityError:
            messages.error(self.request, 'The name {} already in use! Choose another one.'.format(obj.title))
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post/form.html'
    success_url = 'posts-list'


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        return JsonResponse({'result': 1, 'message': 'Post successfully deleted!'})


def new_comment_leave(request):
    domain = get_current_site(request).domain
    recipient_list = [user for user in User.objects.filter(sub_on_comments=True)]
    new_comment_email_send.delay(domain, recipient_list)
    return JsonResponse({})


def unsubscribe_view(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        user.sub_on_comments = False
        user.save()
        return render(request, 'mail_template/unsubscribe_success.html', {})
    else:
        return render(request, 'mail_template/unsubscribe_fail.html', {})
