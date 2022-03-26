from django.shortcuts import render, redirect, reverse
from django.views.decorators.csrf import csrf_exempt

from stream.models import Category, Streamer, UserProfile, User, Comment, SubComment
from stream.forms import UserProfileForm, UserForm, CommentForm, SubCommentForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from stream.webhose_search import run_query

def homepage(request):
    response = render(request, 'stream/homepage.html', context={'categories':Category.objects.all()})
    return response

def about(request):
    return render(request, 'stream/about.html')

def show_category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        streamers = Streamer.objects.filter(category=category)
        context_dict['streamers'] = streamers

        context_dict['category'] = category
        context_dict['query'] = category.name

    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['streamers'] = None

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
            context_dict['query'] = query
            context_dict['result_list'] = result_list

    return render(request, 'stream/category.html', context_dict)

def add_comment(request, name='', category_name_slug=''):
    context_dict = {}
    streamer = Streamer.objects.get(name=name)
    context_dict['streamer'] = streamer
    context_dict['slug'] = category_name_slug
    form = CommentForm()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment_form = form.save(commit=False)
            comment_form.streamer = streamer
            comment_form.user_name = request.user.username
            comment_form.rating = request.POST.get('rating')
            comment_form.text = request.POST.get('text')
            comment_form.save()
            return redirect(reverse('stream:show_streamer',
                                    kwargs={'name': name,
                                            'category_name_slug': category_name_slug, }))
        else:
            print(form.errors)
    context_dict['form'] = form
    return render(request, 'stream/add_comment.html', context_dict)

def add_sub_comment(request,  id=0, name='', category_name_slug=''):
    context_dict = {}
    father_comment = Comment.objects.get(id=id, streamer__name=name)
    context_dict['id'] = id
    context_dict['name'] = name
    context_dict['slug'] = category_name_slug
    form = SubCommentForm()
    if request.method == 'POST':
        form =  SubCommentForm(request.POST)
        if form.is_valid():
            sub_comment_form = form.save(commit=False)
            sub_comment_form.father_comment = father_comment
            sub_comment_form.user_name = request.user.username
            sub_comment_form.text = request.POST.get('text')
            sub_comment_form.save()
            return redirect(reverse('stream:show_streamer',
                                    kwargs={'name': name,
                                            'category_name_slug': category_name_slug,}))
        else:
            print(form.errors)
    context_dict['form'] = form
    return render(request, 'stream/add_sub_comment.html', context_dict)

def show_streamer(request, name='', category_name_slug=''):
    context_dict = {}
    streamer = Streamer.objects.order_by('-views').get(name=name)
    category = Category.objects.get(slug=category_name_slug)
    comments = Comment.objects.filter(streamer=streamer)
    context_dict['comments'] = comments
    context_dict['streamer'] = streamer
    context_dict['category'] = category

    sub_comments = []
    num_of_comments = 0
    total_rating = 0
    for comment in comments:
        num_of_comments += 1
        total_rating += comment.rating
        sub_comments.append(SubComment.objects.filter(father_comment=comment))
    if num_of_comments == 0:
        streamer.rating = 0
    else:
        streamer.rating = round(total_rating / num_of_comments, 2)

    context_dict['sub_comments'] = sub_comments

    return render(request, 'stream/streamer.html', context_dict)

def comment_posted(request):
    return render(request, 'stream/comment_posted.html')

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
                  'stream/register.html',
                  context={'user_form': user_form,
                           'profile_form': profile_form,
                           'registered': registered})

def user_login(request):
    error = None
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('homepage'))
            else:
                error = "Your account is disabled."

        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            error = "Invalid login details supplied."

    return render(request, 'stream/login.html', {'error': error})

@login_required
@csrf_exempt
def edit_profile(request):
    context_dict = {}
    user = request.user
    context_dict['user'] = user
    if request.method == 'POST':
        if request.POST['email']:
            user.email = request.POST.get('email')
        if request.POST['bio']:
            user.userprofile.bio = request.POST.get('bio')
        user.save()
        user.userprofile.save()
        return render(request, 'stream/edit_profile.html', context_dict)
    return render(request, 'stream/edit_profile.html', context_dict)

def view_profile(request, username=''):
    context_dict = {}
    try:
        context_dict['user'] = User.objects.get(username=username)
        context_dict['current_user'] = request.user
        return render(request, 'stream/view_profile.html', context_dict)
    except Exception as e:
        print(e)
        logout(request)
        return HttpResponseRedirect(reverse('homepage'))

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('homepage'))

@login_required
def register_profile(request):
    form = UserProfileForm()
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect('homepage')
        else:
            print(form.errors)
    context_dict = {'form': form}
    return render(request, 'stream/profile_registration.html', context_dict)