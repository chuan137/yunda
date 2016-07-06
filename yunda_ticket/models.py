from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Ticket(models.Model):
    user=models.ForeignKey(User)
    REF_TYPES=(
                ('yde', _('Parcel YDE Number')),
                ('tracking_number', _('YUNDA tracking number')),
                ('retoure_number', _('Retoure label number')),
                ('invoice_number', _('Invoice number')),
                ('others', _('Others')),
                )
    ref_type=models.CharField(max_length=15,null=True,choices=REF_TYPES)
    ref_number=models.CharField(max_length=20,null=True)
    msg=models.TextField()
    created_at=models.DateTimeField()
    is_finished=models.BooleanField(default=False)
    finished_at=models.DateTimeField()

class TicketMsg(models.Model):
    ticket=models.ForeignKey(Ticket)
    is_staff_answer=models.BooleanField(default=False)
    staff=models.ForeignKey(User,limit_choices_to={'is_staff': True})
    msg=models.TextField()