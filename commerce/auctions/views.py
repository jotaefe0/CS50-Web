
from email import message
from queue import Empty
from sre_parse import CATEGORIES
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Auction, User, Bids, Comments, Watchlist

categories = ['Clothes', 'Sports', 'Games', 'Toys', 'Electronics', 'Music','Others']



def index(request):
    a = Auction.objects.filter(isactive=1)
    return render(request, "auctions/index.html", {
        "auctions":a,
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

@login_required
def new(request):
    userid = request.user
    print(f'user: {userid}')
    if request.method == 'POST':
        itemname = request.POST['ItemName']
        initialbid = request.POST['InitialBid']
        category = request.POST['Category']
        description = request.POST['Description']
        imgurl = request.POST['ImgUrl']

        if imgurl == "":
            imgurl = "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"

        if category not in categories:
            return render(request, "auctions/new.html", {
        "categories":categories,
        "message":"Invalid Category"
    })
        if itemname == None or int(initialbid) < 0:
            return render(request, "auctions/new.html", {
        "categories":categories,
        "message":"Please fill out all the requiered fields"
    })
        c = 0
        ## This loop is to get unique listing name, easy way instead of using actual id, so that later we can use the GET info from the browser with name (more visual and user frendly)
        while Auction.objects.filter(itemname=itemname): 
            itemname = itemname + str(c)
            c = c + 1

        a = Auction(owner=userid, itemname=itemname, category=category, imgurl=imgurl, description=description, currentbid=initialbid, isactive=1, winnerid=0)
        a.save()
        
        b = Bids(owner=userid, item=a, bid=initialbid)
        b.save()

        return HttpResponseRedirect(reverse('index'))



    return render(request, "auctions/new.html", {
        "categories":categories
    })


@login_required
def listing(request, listing):
    
    i = Auction.objects.filter(itemname=listing)
    u = request.user
    highestBid = int(Bids.objects.filter(item=i[0]).order_by("-bid")[0].bid)
    highestBidder = (Bids.objects.filter(item=i[0]).order_by("-bid")[0].owner)
    
    try:
        comments = Comments.objects.filter(item=i[0])
        isactive = Auction.objects.filter(itemname=listing)[0].isactive
    except:
        comments = ""


    try:
        W = Watchlist.objects.filter(item=i[0]).filter(user=u)[0].item
        if i[0] == Watchlist.objects.filter(item=i[0]).filter(user=u)[0].item:
            addremovevalue = 'Remove from'
            addremove = 'remove'
    except:
        addremovevalue = 'Add to'
        addremove = 'add'
    
    try:
        listingurl = i[0].itemname
    except:
        listingurl = ""
    try:
        owner = i[0].owner == u
    except:
        owner = False
    #add listing
    if request.method == 'POST' and 'add' in request.POST:
        w = Watchlist(user=u, item=i[0])
        w.save()
        print("adding")
        return HttpResponseRedirect(reverse('listing', kwargs={'listing': listing}))

    #remove listing
    elif request.method == 'POST' and 'remove' in request.POST:
        w = Watchlist.objects.filter(item=i[0]).filter(user=u)
        w.delete()
        print('removing')
        return HttpResponseRedirect(reverse('listing', kwargs={'listing': listing}))

    #place bid, checks highest bid and compare
    if request.method == 'POST' and 'Bid' in request.POST and isactive:
        bid = request.POST['Bid']
        b = Bids(owner=u, item=i[0], bid=bid)
        a = Auction(id=i[0].id, currentbid=bid)
        highestBid = int(Bids.objects.filter(item=i[0]).order_by("-bid")[0].bid)
        if int(bid) > highestBid:
            b.save()
            a.save(update_fields=['currentbid'])
            message = f"Your Bid of {bid}$ has been placed!"
        else:
            message = f"Your Bid needs to be higher than {highestBid} in order to place you Bid"
        print(f'bidding for {bid} for {listingurl}')

        return render(request, "auctions/listing.html", {
        "alisting":i,
        "listingurl":listingurl,
        "addremove":addremove,
        "addremovevalue":addremovevalue,
        "message":message,
        "owner":owner,
        "isactive":isactive,
        "comments":comments
    })
    #close Listing
    try:
        owner = i[0].owner == u
    except:
        owner = False
    
    if request.method == 'POST' and 'close' in request.POST and owner:
        a = Auction(id=i[0].id, isactive=0)
        a.save(update_fields=['isactive'])
        print("closing Listing")
        return HttpResponseRedirect(reverse('listing', kwargs={'listing': listing}))

    #Checks if Listing is Active and who is the winner
    try: 
        isactive = Auction.objects.filter(itemname=listing)[0].isactive
        if isactive == False:
            highestBid = int(Bids.objects.filter(item=i[0]).order_by("-bid")[0].bid)
            highestBidder = (Bids.objects.filter(item=i[0]).order_by("-bid")[0].owner)
            print(highestBid)
            print(highestBidder.username)
            if highestBidder == u:
                highestBidder = "You are the winner"
            else:
                highestBidder = f"{highestBidder.username} has won this listing"
    except:
        pass
    #Comments
    if request.method == 'POST' and 'comment' in request.POST:
        print("comment")
        i = Auction.objects.filter(itemname=listing)
        comment = request.POST["comment"]
        print(comment)
        c = Comments(item=i[0], itemcomment=comment)
        c.save()

    #Render
    return render(request, "auctions/listing.html", {
        "listing":listing,
        "alisting":i,
        "listingurl":listingurl,
        "addremove":addremove,
        "addremovevalue":addremovevalue,
        "owner":owner,
        "isactive":isactive,
        "winner":highestBidder,
        "highestbid":highestBid,
        "comments":comments
    })


@login_required
def watchlist(request):
    u = request.user
    w = Watchlist.objects.filter(user=u)
    try:
        print(w[0].item)
    except:
        return render(request, "auctions/watchlist.html", {
        "message":"There are no items in your watchlist"
    })
    print(f"length of wl {len(w)}")
    return render(request, "auctions/watchlist.html", {
        "watchlist":w
    })


@login_required
def categoriesf(request):
    
    return render(request, "auctions/categories.html", {
        "categories":categories
    })

@login_required
def categoriesp(request, category):
    categories = Auction.objects.filter(category=category).filter(isactive=1)
    return render(request, "auctions/category.html", {
        "categories":categories
    })

    

