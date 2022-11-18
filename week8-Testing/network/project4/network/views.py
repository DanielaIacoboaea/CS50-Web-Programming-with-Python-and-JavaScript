from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.paginator import Paginator

from .models import User, Post, Comment, Follower, Like


# user form to create a new post 
class AddPost(forms.Form):
    content = forms.CharField(label="Content", widget=forms.Textarea(attrs={
        'placeholder': "What's happening?", 'class': 'add-post-content'}), max_length=300)
    image = forms.ImageField(label="Image", required=False)


@csrf_exempt
def index(request):

    """
    Load all posts, comments and likes for each post 
    Differentiate between posts liked by the user and other posts
    """

    if request.user.is_authenticated:
        
        # Display all posts 
        if request.method == 'GET':
            
            # Django paginator documentation
            # Use to display 10 posts/page 
            # and allow user to toggle between pages
            posts = Post.objects.all()
            paginator = Paginator(posts, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            # check all likes for active user 
            # use in template to check for each post if the user liked the post 
            userLikes = list(posts)
            for post in userLikes:
                post.is_liked = post.likes.filter(likedBy=request.user).exists()
            
            return render(request, "network/index.html", {
                'posts': posts,
                'likes': Like.objects.all(),
                'comments': Comment.objects.all(),
                'form': AddPost(),
                'userLiked': userLikes,
                'page_obj': page_obj
            })
        # Save new post created by user
        else:
            form = AddPost(request.POST, request.FILES)
            if form.is_valid():
                content = form.cleaned_data['content']
                image = form.cleaned_data['image']
                if image:
                    addPost = Post.objects.create(owner=request.user, content=content, image=image)
                    addPost.save()
                else:
                    addPost = Post.objects.create(owner=request.user, content=content)
                    addPost.save()
                return HttpResponse(status=204)
    else:
        return HttpResponseRedirect(reverse("login"))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def following(request):

    """
    Load posts only for other users that 
    the active user follows 
    """

    # check if the user follows other users
    try: 
        follower = Follower.objects.get(follower = request.user)
        follows = follower.follows.all()

        # check if the owner of the post is among the 
        # users that the active user follows 
        # load only posts with this property 
        posts = Post.objects.filter(owner__in= follows)
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        userLikes = list(posts)
        for post in userLikes:
            post.is_liked = post.likes.filter(likedBy=request.user).exists()

        return render(request, "network/index.html", {
            'posts': Post.objects.filter(owner__in= follows),
            'likes': Like.objects.all(),
            'comments': Comment.objects.all(),
            'page_obj': page_obj,
            'userLiked': userLikes,
            'form': AddPost()
        })
    # if the user does not follow anyone,
    # display all posts  
    except:
        return HttpResponseRedirect(reverse("index"))



@csrf_exempt
@login_required
def profile(request, user_id):

    """
    Display the selected user profile
    Profile elements: followers, following, all posts 
    If the active user is different than the user profile, 
    display additional information: follow/following  

    """

    user = User.objects.get(pk=user_id)

    if request.method == 'GET':

        # display only the posts added by the user (user profile)
        posts = Post.objects.filter(owner = user)
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        userLikes = list(posts)
        for post in userLikes:
            post.is_liked = post.likes.filter(likedBy=request.user).exists()

        following = Follower.objects.get(follower = user)

        # check if the active user follows the user
        # from user profile and display follow/following buttons accordingly 
        # active user follows profile user
        return render(request, "network/profile.html", {
            'userProfile': user,
            'follows': following.follows.count(),
            'followers': user.followers.count(),
            'posts': Post.objects.filter(owner = user),
            'likes': Like.objects.all(),
            'comments': Comment.objects.all(),
            'followBtn': user.followers.filter(follower = request.user).exists(),
            'page_obj': page_obj,
            'userLiked': userLikes
        })

    # add or remove active user as follower
    elif request.method == 'POST':
        followUserProfile = json.loads(request.body)
        follow = followUserProfile.get('follow')
        unfollow = followUserProfile.get('unfollow')

        if follow:
            # check if the user is already in the db, following someone else 
            # in this case, just update the entry and add the user profile to it
            try: 
                followUser = Follower.objects.get(follower=request.user)
                followUser.follows.add(user)
                followUser.save()
            # otherwise create a new entry for the active user 
            except:
                followUser = Follower(follower=request.user)
                followUser.save()
                followUser.follows.add(user)
                followUser.save()
        # remove active user from the followers list 
        if unfollow:
            unfollowUser = Follower.objects.get(follower=request.user)
            unfollowUser.follows.remove(user)
        return HttpResponse(status=204)

    # allow user to edit the text for a post created by them 
    # save the changes to the database
    else: 
        newPostContent = json.loads(request.body)
        updateText = newPostContent.get('newContent')
        updatePostId = newPostContent.get('postId')

        # check if the user making the edit request 
        # is the owner of the post 
        # check if the content is valid, the entry exists 
        if request.user == user:
            if updateText:
                post = Post.objects.get(owner=request.user, pk=updatePostId)
                if post:
                    post.content = updateText
                    post.save()
                    return HttpResponse(status=204)
                else:
                    return HttpResponse(status=404)
            else:
                return HttpResponse(status=404)
        else:
            return HttpResponse(status=404)



@csrf_exempt
def likes(request, post_id):

    """
    Save a user like for a post
    or delete it, based on request 
    """

    if request.method == 'POST':
        post = Post.objects.get(pk=post_id)
        likeInfo = json.loads(request.body)
        like = likeInfo.get('like')
        if like == 'like':
            likePost = Like.objects.create(postLiked=post, likedBy=request.user)
            likePost.save()
        elif like == 'unlike':
            unlikePost = Like.objects.get(postLiked=post, likedBy=request.user)
            unlikePost.delete()
    return HttpResponse(status=204)


@csrf_exempt
def comments(request):

    """
    Add comments for a post.
    """

    if request.method == 'POST':
        commentContent = request.POST.get('addComment', False)
        commentPostId = request.POST.get('comment-post-id', False)

        if commentContent and commentPostId:
            post = Post.objects.get(pk=int(commentPostId))
            addComment = Comment.objects.create(post=post, user=request.user, text=commentContent)
            addComment.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return HttpResponse(status=404)
