from statistics import mode
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    
    def __str__(self):
        return f"{self.id} ({self.username})"

class Auction(models.Model):
    itemname = models.CharField(max_length=64)
    owner =  models.ForeignKey(User, on_delete=models.CASCADE, related_name="itemowner")
    category = models.CharField(max_length=64)
    imgurl =  models.CharField(max_length=1000)
    description = models.CharField(max_length=1000)
    currentbid = models.IntegerField()
    isactive = models.BooleanField()
    winnerid = models.IntegerField()

    def __str__(self):
        return f"{self.itemname} published by {self.owner} ({self.category})"

class Bids(models.Model):
    owner =  models.ForeignKey(User, on_delete=models.CASCADE, related_name="itembidder")
    item = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="itembid")
    bid = models.IntegerField()
    

    def __str__(self):
        return f"{self.owner} bid {self.item} for {self.bid} $"

class Comments(models.Model):
    item = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="itemcomment")
    itemcomment = models.CharField(max_length=1000)
 

    def __str__(self):
        return f"{self.itemcomment}"

class Watchlist(models.Model):
    user =  models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    item = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="item")

    def __str__(self):
        return f"{self.user} {self.item}"