from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"



class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=150)
    date = models.DateField(auto_now_add=True, blank=True)
    start_bid = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.URLField(max_length=245, blank=True)

    initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="category")

    LISTING_STATUS = (
        ('a', 'Active'),
        ('c', 'Closed')
    )
    status = models.CharField(max_length=15, choices=LISTING_STATUS, default='a', help_text="Listing Status")

    def __str__(self):
        return f"Listing {self.id}: {self.title} by {self.initiator} on {self.date}"



class Winner(models.Model):
    entry = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="won")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="winner", blank=True)
    winning_bid = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Listing: {self.entry.title}: winner: {self.winner.username}, bid: {self.winning_bid}"



class Bid(models.Model):
    value = models.DecimalField(max_digits=8, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bidListing")

    def __str__(self):
        return f"Bid ${self.value} for {self.listing.title} by {self.bidder.username}"



class Comment(models.Model):
    content = models.TextField(max_length=150)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="creator")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"Comment: {self.content}, for: {self.listing.title} by {self.creator.username}"



class WatchList(models.Model):
    listings = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchListing")
    users = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchUser")

    def __str__(self):
        return f"Listing: {self.listings.title} for {self.users.username}"








