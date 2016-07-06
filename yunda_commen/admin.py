from django.contrib import admin
from yunda_commen.models import Sequence, Settings

# Register your models here.
class SequenceAdmin(admin.ModelAdmin):
    fieldset = [
              (None, {'fields':['code']}),
              (None, {'fields':['next_value', 'interval']}),
              (None, {'fields':['prefix', 'suffix']}),
              (None, {'fields':['digit_length', ]}),
              (None, {'fields':['renew_type']}),
              ]

admin.site.register(Sequence, SequenceAdmin)

class SettingsAdmin(admin.ModelAdmin):
    pass

admin.site.register(Settings, SettingsAdmin)
