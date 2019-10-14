from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post, User


class PostsListUIView(ListView):
    model = Post
    template_name = 'ui/post_list.html'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().filter(published=True)


class PostUIView(DetailView):
    template_name = 'ui/post.html'
    model = Post

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     print(context)
    #     return render(self.request, self.template_name, context)
