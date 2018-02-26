from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (TemplateView, ListView, DeleteView, DetailView, UpdateView, CreateView)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from docs.models import Post, Comment
from docs.forms import PostForm, CommentForm, SignUpForm
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.contrib.auth import login, authenticate


# Create your views here.

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('docs:post_list')
    else:
        form = SignUpForm()
    return render(request, 'docs/register_form.html', {'form': form})



class DocsSearchListView(ListView):
    '''
    Display a docs list page filtered by search query
    '''
    model = Post
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        keywords = self.request.GET.get('q')
        if keywords:
            query = SearchQuery(keywords)
            vector = SearchVector('title', 'text')
            qs = qs.annotate(search=vector).filter(search=query)

            qs = qs.annotate(rank=SearchRank(vector, query)).order_by('-rank')
            print("qs {}".format(qs.__dict__))
        return qs

        # def get_context_data(self, **kwargs):
        #     return super().get_context_data(q=self.request.GET.get('q', ""))


class AboutView(TemplateView):
    template_name = 'docs/about.html'


class PostListView(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')

class PostDetailView(DetailView):
    model = Post

class CreatePostView(CreateView, LoginRequiredMixin):
    login_url = '/login'
    redirect_field_name = 'docs/post_detail.html'
    form_class = PostForm
    model = Post

class DraftListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'docs/post_draft_list.html'
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('create_date')

class PostUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    redirect_field_name = 'docs/post_detail.html'
    form_class = PostForm
    model = Post

    #TODO Add the autoselect Username
    # def form_valid(self, form):
    #     form.author_id = self.request.user
    #     return super().form_valid(form)

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('docs:post_list')

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('docs:post_list')


@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('docs:post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'docs/comment_form.html', {'form': form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    # print("beforecommit: {}".format(comment.__dict__)) #TEST
    comment.approve()
    # print("aftercommit: {}".format(comment.__dict__))  # TEST
    return redirect('docs:post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('docs:post_detail', pk=post_pk)
