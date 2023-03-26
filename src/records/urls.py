from django.urls import path, re_path
from .views import (
    add_entry, all_entries, detail_entry, edit_entry, delete_entry, open_image, send_entry,
    APIEntries, APICreateEntry, APIUpdateEntry, APIDeleteEntry,
    delete_voice_record, my_public_diaries, create_new_diary, all_public_diaries
)


urlpatterns = [
    path('add_entry/', add_entry, name='add_entry'),
    path('my_public_diaries/', my_public_diaries, name='my_public_diaries'),
    path('create_new_diary/', create_new_diary, name='create_new_diary'),
    path('all_public_diaries/', all_public_diaries, name='all_public_diaries'),
    path('all_entries/', all_entries, name='all_entries'),
    path('details_entry/<int:entry_id>/', detail_entry, name='detail_entry'),
    path('edit_entry/<int:entry_id>/', edit_entry, name='edit_entry'),
    path('delete_entry/<int:entry_id>/', delete_entry, name='delete_entry'),
    path('open_image/<int:entry_id>/', open_image, name='open_image'),
    path('send_entry/<int:entry_id>/', send_entry, name='send_entry'),
    path('api/entries/', APIEntries.as_view()),
    path('api/entry/create/', APICreateEntry.as_view()),
    path('api/entry/update/<int:pk>/', APIUpdateEntry.as_view()),
    path('api/entry/delete/<int:pk>/', APIDeleteEntry.as_view()),
    re_path(r'^page/(\d+)/$', all_entries, name='all_entries'),
    path('delete_voice_record/<int:entry_id>/', delete_voice_record, name='delete_voice_record'),
]
