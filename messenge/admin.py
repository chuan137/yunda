from django.contrib import admin
from messenge import models

# Register your models here.
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'has_unread_messenge','has_staff_unread','created_by_stuff','created_at')
    list_filter = ('user', 'created_by_stuff', 'has_unread_messenge','has_staff_unread')
admin.site.register(models.Subject, SubjectAdmin)

class MessengeAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Messenge, MessengeAdmin)