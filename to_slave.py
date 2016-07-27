from django.contrib.contenttypes.models import ContentType
import logging

def run():

 def do(Table):
  if Table is not None:
   table_objects = Table.objects.all()
   for i in table_objects:
    try:
     i.save(using='slave')
    except:
     logging.exception('error')
 
 ContentType.objects.using('slave').all().delete()

 for i in ContentType.objects.all():
  do(i.model_class())
