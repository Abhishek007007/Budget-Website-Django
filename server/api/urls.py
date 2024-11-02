from django.urls import path, include
from .views.main.main_views import IncomeSourceView, IncomeView, CategoryView, ExpenseView
from .views.Auth.auth_view import UserRegistrationView, UserLoginView, LogoutView, PasswordChangeView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView


router = DefaultRouter()
router.register(r'source', IncomeSourceView, basename='source')
router.register(r'income',  IncomeView, basename='income')
router.register(r'category', CategoryView, basename='catagory')
router.register(r'expense', ExpenseView, basename='expense')


urlpatterns = [
    # User Authentication
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view() , name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_change/', PasswordChangeView.as_view(), name='password_change'),

    # Income AP
    
    
    path('finance/', include(router.urls)),
]
