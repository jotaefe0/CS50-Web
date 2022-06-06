from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("categories", views.categoriesf, name="categoriesf"),
    path("register", views.register, name="register"),
    path("new", views.new, name="new"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("<str:listing>", views.listing, name="listing"),
    path("categories/<str:category>", views.categoriesp, name="categoriesp"),
]
