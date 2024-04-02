"""
URL configuration for trixbank project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from core.views import LandingPageView,logoutView,AboutPageView,changePasswordView,updateProfileView,loginView,registerView,dashboardView,depositView,withdrawView,transferView,historyView,deposit_partial,withdraw_partial,transfer_partial,notificationView,profileView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',LandingPageView.as_view(),name="landing"),
    path('login/',loginView,name="login"),
    path('logout/',logoutView,name="logout"),
    path('about/',AboutPageView.as_view(),name='about'),
    path('sign-in/',registerView,name="sign-in"),
    path('dashboard/',dashboardView,name="dashboard"),
    path('dashboard/deposit/',depositView,name="deposit"),
    path('dashboard/widthdraw/',withdrawView,name="withdraw"),
    path('dashboard/transfer/',transferView,name="transfer"),
    path('dashboard/history/',historyView,name="history"),
    path('dashboard/notifications/',notificationView,name="notifications"),
    path('dashboard/profile/',profileView,name="profile"),
    path('dashboard/profile/update/',updateProfileView,name="update-profile"),
    path('dashboard/profile/change-password/',changePasswordView,name="change-password"),
    path('partials/transfer/',transfer_partial,name="transfer-partial"),
    path('partials/withdraw/',withdraw_partial,name="widthdraw-partial"),
    path("partials/deposit/",deposit_partial,name="deposit-partial"),
    
    
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
