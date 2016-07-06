# -*- coding: utf-8 -*-
import hashlib
from parcel.models import IntlParcel
from yunda_parcel.models import SenderTemplate, ReceiverTemplate
## Set all Yid
def setIntlParcelAllYid():
    for parcel in IntlParcel.objects.all():
        parcel.yid=hashlib.md5("intlparcel%d" % parcel.id).hexdigest()
        parcel.save()

def setSenderTemplateAllYid():
    for obj in SenderTemplate.objects.all():
        obj.yid=hashlib.md5("sendertemplate%d" % obj.id).hexdigest()
        obj.save()

def setReceiverTemplateAllYid():
    for obj in ReceiverTemplate.objects.all():
        obj.yid=hashlib.md5("receivertemplate%d" % obj.id).hexdigest()
        obj.save()