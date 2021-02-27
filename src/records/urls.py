from django.urls import path
from .views import add_record, all_records, detail_record, edit_record, \
    delete_record, open_image, send_record, APIRecords, APICreateRecord, APIUpdateRecord, APIDeleteRecord

from django.conf.urls import url

urlpatterns = [
    path('add_record/', add_record, name='add_record'),
    path('all_records/', all_records, name='all_records'),
    path('detail_record/<int:record_id>/', detail_record, name='detail_record'),
    path('edit_record/<int:record_id>/', edit_record, name='edit_record'),
    path('delete_record/<int:record_id>/', delete_record, name='delete_record'),
    path('open_image/<int:record_id>/', open_image, name='open_image'),
    path('send_record/<int:record_id>/', send_record, name='send_record'),
    path('api/records/', APIRecords.as_view()),
    path('api/record/create/', APICreateRecord.as_view()),
    path('api/record/update/<int:pk>/', APIUpdateRecord.as_view()),
    path('api/record/delete/<int:pk>/', APIDeleteRecord.as_view()),
    url(r'^page/(\d+)/$', all_records, name='all_records'),
    ]


