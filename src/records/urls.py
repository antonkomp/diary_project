from django.urls import path, re_path
from .views import add_record, all_records, detail_record, edit_record, \
     delete_record, open_image, send_record, APIRecords, APICreateRecord, APIUpdateRecord, APIDeleteRecord, \
     delete_voice_record, my_public_diaries, create_new_diary, all_public_diaries


urlpatterns = [
    path('add_entry/', add_record, name='add_record'),
    path('my_public_diaries/', my_public_diaries, name='my_public_diaries'),
    path('create_new_diary/', create_new_diary, name='create_new_diary'),
    path('all_public_diaries/', all_public_diaries, name='all_public_diaries'),
    path('all_entries/', all_records, name='all_records'),
    path('details_entry/<int:record_id>/', detail_record, name='detail_record'),
    path('edit_entry/<int:record_id>/', edit_record, name='edit_record'),
    path('delete_entry/<int:record_id>/', delete_record, name='delete_record'),
    path('open_image/<int:record_id>/', open_image, name='open_image'),
    path('send_entry/<int:record_id>/', send_record, name='send_record'),
    path('api/entries/', APIRecords.as_view()),
    path('api/entry/create/', APICreateRecord.as_view()),
    path('api/entry/update/<int:pk>/', APIUpdateRecord.as_view()),
    path('api/entry/delete/<int:pk>/', APIDeleteRecord.as_view()),
    re_path(r'^page/(\d+)/$', all_records, name='all_records'),
    path('delete_voice_record/<int:record_id>/', delete_voice_record, name='delete_voice_record'),
    ]
