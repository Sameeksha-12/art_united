from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login,authenticate
from django.contrib.auth.decorators import login_required
from .forms import BlogPostForm,CommentForm,SavePostForm
from .models import BlogPost, Comment,SavedPost
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime

# Create your views here.
def index(request):
    return render(request,'index.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request,'signup.html',{'form':form})

def signin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request,data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'signin.html',{'form':form})


@login_required
def home(request):
    blog_posts = BlogPost.objects.all()
    return render(request,'home.html',{'blog_posts':blog_posts})

@login_required
def create_blog(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the blog post and redirect to the home page
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            blog_post.created_at = timezone.now()
            blog_post.save()
            return redirect('home')
    else:
        form = BlogPostForm()

    return render(request, 'create_blog.html', {'form': form})

@login_required
def show(request, blog_id):
    blog_post = BlogPost.objects.get(pk=blog_id)
    comments = Comment.objects.filter(blog_post=blog_post)
    similar_posts = BlogPost.objects.filter(category=blog_post.category).exclude(id=blog_id)[:5]
    save_post_form = SavePostForm()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.blog_post = blog_post
            new_comment.author = request.user
            new_comment.save()
            return redirect('show',blog_id=blog_id)
        elif 'save_post' in request.POST:
            # Check if the post is already saved by the user
            if SavedPost.objects.filter(user=request.user, post=blog_post).exists():
                messages.warning(request, 'Blog post is already saved.')
            else:
                # Save the post for the logged-in user
                saved_post = SavedPost.objects.create(user=request.user, post=blog_post)
                messages.success(request, 'Blog post saved successfully.')
    else:
        form = CommentForm()
    return render(request,'show.html',{'blog_post':blog_post,'comments': comments, 'form':form, 'similar_posts':similar_posts, 'save_post_form':save_post_form})

    

def user_profile(request, username):
    user_posts = BlogPost.objects.filter(author__username=username)
    current_date = datetime.now().strftime("%B %d, %Y")
    saved_posts = SavedPost.objects.filter(user=request.user)
    return render(request, 'profile.html', {'current_date': current_date,'user_posts': user_posts, 'username': username , 'saved_posts':saved_posts})

def explore(request):
    current_date = datetime.now().strftime("%B %d, %Y")
    category_choices = BlogPost.CATEGORY_CHOICES
    return render(request,'explore.html',{'current_date': current_date,'category_choices':category_choices})

def category_posts(request,category_value):
    posts = BlogPost.objects.filter(category=category_value)
    context = {'category_value':category_value, 'posts':posts}
    return render(request,'category_posts.html',context)