from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max
from django import forms

from .models import User, Category, Listing, Winner, Bid, Comment, WatchList

# Define form for a new Listing creation 
class CreateListing(forms.Form):
    title = forms.CharField(label="Title", 
        widget=forms.TextInput(attrs={'placeholder': 'New title'}))
    description = forms.CharField(label="Description", widget=forms.Textarea(attrs={
        'placeholder': 'Describe your listing'}))
    startingBid = forms.DecimalField(label="Starting Bid")
    category = forms.CharField(label="Category", 
        widget=forms.TextInput(attrs={'placeholder': 'Category'}), required=False)
    image = forms.URLField(label="Provide link to image", required=False)


# Define form for User interaction on a Listing's page 
class ListingInteraction(forms.Form):
    bid = forms.DecimalField(label="Bid", required=False)
    closeListing = forms.MultipleChoiceField(label="Close Listing", 
        required=False, widget=forms.CheckboxSelectMultiple, choices=[("close", "Close")])
    addComment = forms.CharField(label="Add Comment", required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Comment'}))
    watchList = forms.MultipleChoiceField(label="Watchlist", required=False, 
        widget=forms.CheckboxSelectMultiple, choices=[("add", "Add"),("remove", "Remove")])


def index(request):
    """ 
    List all active auction listings.
    List closed auctions only for users that won them.
    """

    activeListings = Listing.objects.all().filter(status = 'a')

    #Find the current highest price
    for listing in activeListings:
        bids = Bid.objects.all().filter(listing = listing.id).aggregate(max_bid=Max('value'))['max_bid']
        if bids is None:
            bids = listing.start_bid
        else:
            listing.start_bid = f"{bids:.2f}"
    
    # Check if a winner is authenticated before displaying
    # a closed listing
    if request.user.is_authenticated:
        closedListings = []
        userWinnings = Winner.objects.all().filter(winner = request.user)
        if userWinnings:
            for listing in userWinnings:
                getListing =  Listing.objects.all().filter(pk = listing.entry.id)
                closedListings.append(getListing)
            return render(request, "auctions/index.html", {
                "listings": activeListings,
                "closedListings": closedListings
            })

    # otherwise just render the active listings 
    return render(request, "auctions/index.html", {
        "listings": activeListings
    })


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")




def listing(request, listing_id):
    """
    Display all the details for the required Listing.
    Allow users to place bids for that Listing,
    add comments, add/remove the Listing from a Watchlist 
    and close the Listing if they are owners of that Listing 
    """

    # Display all details for the Listing 
    if request.method == 'GET':
        listing = Listing.objects.get(pk=listing_id)
        bids = Bid.objects.all().filter(listing = listing.id).aggregate(max_bid=Max('value'))['max_bid']
        if bids is None:
            bids = listing.start_bid
        else:
            bids = f"{bids:.2f}"
        comments = Comment.objects.all().filter(listing = listing.id)
        category = Listing.objects.values('category')
        category_name = Category.objects.get(name=listing.category)
        if request.user == listing.initiator:
            owner = True
        else:
            owner = False
        context = {
            'listing': listing,
            'comments': comments,
            'category': category_name,
            'highestBid': bids,
            'form': ListingInteraction(),
            'owner': owner
        }
        return render(request, "auctions/listing.html", context)
    else: 
        # Check the user input for change requests 
        form = ListingInteraction(request.POST)
        listing = Listing.objects.get(pk=listing_id)
        comments = Comment.objects.all().filter(listing = listing.id)
        category = Listing.objects.values('category')
        category_name = Category.objects.get(name=listing.category)
        if request.user == listing.initiator:
            owner = True
        else:
            owner = False
        if form.is_valid():
            bid = form.cleaned_data['bid']
            closeListing = form.cleaned_data['closeListing']
            addComment = form.cleaned_data['addComment']
            watchList = form.cleaned_data['watchList']

            # Bids
            # Check the bid against all bids placed on this Listing 
            # and against the original price before recording it 
            bids = Bid.objects.all().filter(listing = listing.id).aggregate(max_bid=Max('value'))['max_bid']
            if bid:
                if bids is None:
                    bids = f"{listing.start_bid:.2f}"
                if bid > bids:
                    bid = f"{bid:.2f}"
                    addBid = Bid.objects.create(value=bid, bidder=request.user, listing=listing)
                    addBid.save()
                else:
                    return render(request, "auctions/listing.html", {
                "message": "You bid is lower than the current price.",
                'listing': listing,
                'comments': comments,
                'category': category_name,
                'highestBid': f"{bids:.2f}",
                'form': ListingInteraction(),
                'owner': owner
                })
            else:
                if bids is None:
                    bids = listing.start_bid

            #Comments
            if addComment:
                newComment = Comment.objects.create(content=addComment, creator=request.user, listing=listing)
                newComment.save()
            
            # Add/Remove from watchlist 
            # Render error message if the listing is already on the watchlist 
            if watchList:
                if watchList[0] == 'add':
                    try:
                        checkIfExists = WatchList.objects.get(listings=listing, users=request.user)
                        return render(request, "auctions/listing.html", {
                        "message": "Listing already on your Watchlist.",
                        'listing': listing,
                        'comments': comments,
                        'category': category_name,
                        'highestBid': bids,
                        'form': ListingInteraction(),
                        'owner': owner
                        })
                    except:
                        addWatchlist = WatchList.objects.create(listings=listing, users=request.user)
                        addWatchlist.save()
                elif watchList[0] == 'remove':
                    removeWatchList = WatchList.objects.get(listings=listing, users=request.user)
                    removeWatchList.delete()
            
            # Close a listing 
            # Option available only for the user that created the Listing 
            if closeListing:
                if closeListing[0] == 'close':
                    # Update status
                    listing.status = 'c'
                    listing.save()

                    # Find winner and update the database with the winner 
                    highest = Bid.objects.all().filter(listing = listing.id).aggregate(max_bid=Max('value'))['max_bid']
                    highestBider = Bid.objects.get(value=highest, listing = listing.id)
                    userWinner = User.objects.get(pk=highestBider.bidder.id)
                    winner = Winner.objects.create(entry=listing, winner=userWinner, winning_bid=highest)
                    winner.save()

                    # Remove Listing from Watchlist if it exists 
                    try:
                        checkIfOnWatchList = WatchList.objects.get(listings=listing, users=userWinner)
                        checkIfOnWatchList.delete()
                    except: 
                        pass
                    return HttpResponseRedirect(reverse("index"))
            return render(request, "auctions/listing.html", {
                "message": "Changes successfully saved",
                'listing': listing,
                'comments': comments,
                'category': category_name,
                'highestBid': f"{bids:.2f}",
                'form': ListingInteraction(),
                'owner': owner
                })


def create(request):
    """
    Allow users to create listings.
    """

    if request.method == 'POST':

        # Retrieve details for the new Listing 
        form = CreateListing(request.POST)
        if form.is_valid():
            newTitle = form.cleaned_data['title']
            newDescription = form.cleaned_data['description']
            price = form.cleaned_data['startingBid']
            newCategory = form.cleaned_data['category']
            newImage = form.cleaned_data['image']
            newInitator = request.user

            # Check if a category is mentioned
            # Otherwise asign 'No category' by default 
            if newCategory:
                try:
                    existingCategory = Category.objects.get(name = newCategory)
                    newCategoryId = Category.objects.get(pk = existingCategory.id)
                except:
                    addCategory = Category.objects.create(name=newCategory)
                    addCategory.save()
                    newCategoryId = Category.objects.get(pk = addCategory.id)
                newListing = Listing.objects.create(title=newTitle, description=newDescription, start_bid=price, image=newImage, initiator=newInitator, category=newCategoryId)
                newListing.save()
            else:
                defaultCategory = Category.objects.get(name = "No category")
                newListing = Listing.objects.create(title=newTitle, description=newDescription, start_bid=price, image=newImage, initiator=newInitator, category=defaultCategory)
                newListing.save()
        return HttpResponseRedirect(reverse("index"))
    else: 
        return render(request, "auctions/create.html", {
            'form': CreateListing()
        })


def categories(request):
    """
    List all categories available,
    including 'No category' category.
    """

    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })


def category(request, category_id):
    """
    Display all available Listings withing the requested category.
    """

    category = Category.objects.get(pk=category_id)
    categoryListings = Listing.objects.all().filter(category=category, status='a')
    return render(request, "auctions/index.html", {
        "listings": categoryListings
    })


def watchlist(request):
    """
    Display all Listings added on a users's Watchlist.
    """

    watchlist = WatchList.objects.all().filter(users = request.user)
    activeListings = []
    for listing in watchlist:
        getListing =  Listing.objects.all().filter(pk = listing.listings.id)
        activeListings.append(getListing)
    return render(request, "auctions/watchlist.html", {
        "listings": activeListings
    })