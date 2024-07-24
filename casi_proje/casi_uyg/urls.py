from django.urls import path
from . import views

urlpatterns = [
    path("",views.index,name="index"),
    path("gunler/",views.gunler,name="gunler"),
    path("oyunlar/",views.oyunlar,name="oyunlar"),
    path("zaman/",views.zaman,name="zaman"),
    path("bahis_miktar/",views.bahis_miktar,name="bahis_miktar"),
    path("son_oyunlar/",views.son_oyunlar,name="son_oyunlar"),
]