from django.urls import path

from .views import process_get_view, user_form, handle_file_upload

app_name = 'requestdataapp'

urlpatterns = [
    path('upload/', handle_file_upload, name='file_upload'),
    path('get/', process_get_view, name='get_view'),
    path('bio/', user_form, name='user_form'),
]

