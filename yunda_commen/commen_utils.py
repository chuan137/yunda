from models import Sequence
from datetime import datetime
from yunda_commen.models import Settings
from django.conf import settings as django_settings
import xmlrpclib

def _get_check_digit(number):
    # _code = str(code)
    a = 0
    b = 0
    d = True
    for c in str(number):
        if d:
            a += int(c)
        else:
            b += int(c)
        d = not d
    a = a * 4 + b * 9
    a = str(a)
    if a[len(a) - 1:] == '0':
        return "0"
    else:
        return str(10 - int(a[len(a) - 1:]))

def get_seq_by_code(code, with_check_digit=False):
    seq = Sequence.objects.get(code=code)
    if seq.renew_type == "Y" and seq.last_datetime.year != datetime.now().year:
        seq.next_value = 1
        seq.save()
        seq = Sequence.objects.get(code=code)
    elif seq.renew_type == "M" and seq.last_datetime.month != datetime.now().month:
        seq.next_value = 1
        seq.save()
        seq = Sequence.objects.get(code=code)
    elif seq.renew_type == "D" and seq.last_datetime.day != datetime.now().day:
        seq.next_value = 1
        seq.save()
        seq = Sequence.objects.get(code=code)
    prefix = datetime.now().strftime(seq.prefix or '')
    suffix = datetime.now().strftime(seq.suffix or '')
    current_value = seq.next_value    
    if seq.digit_length:
        result = "%0" + str(seq.digit_length) + "d"
    else:
        result = "%d"
    result = result % current_value
    if with_check_digit:
        result = result + _get_check_digit(current_value)
    result = prefix + result + suffix    
    seq.next_value = current_value + seq.interval
    seq.last_datetime = datetime.now()
    seq.save()
    return result

def get_settings():
    return Settings.objects.get(code="default")
        
    

def get_retoure_price(currency_type):
    if currency_type=="eur":
        return Settings.objects.get(code="default").dhl_retoure_price_eur
    else:
        return Settings.objects.get(code="default").dhl_retoure_price_cny

def deposit_deduct(customer_number, origin, comment, amount):
    url = getattr(django_settings, 'ODOO_URL', 'localhost:8069')
    username = getattr(django_settings, 'ODOO_USERNAME', '')
    password = getattr(django_settings, 'ODOO_PASSWORD', '')
    uid = getattr(django_settings, 'ODOO_UID', -1)
    db = getattr(django_settings, 'ODOO_DB', '')
    try:
        if uid < 1:
            common = xmlrpclib.ServerProxy('%s/xmlrpc/2/common' % url)
            uid = common.authenticate(db, username, password, {})
        models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % url)
    
        result = models.execute_kw(db, uid, password,
            'res.partner', 'direct_deduct_by_customer_number',
            [],
            {'customer_number': customer_number, 
             'vals':{
                     'amount':amount,
                     'origin':origin,
                     'comment':comment,
                     }
             })
        return result
    except:
        return False
    
def deposit_increase(customer_number, origin, comment, amount):
    url = getattr(django_settings, 'ODOO_URL', 'localhost:8069')
    username = getattr(django_settings, 'ODOO_USERNAME', '')
    password = getattr(django_settings, 'ODOO_PASSWORD', '')
    uid = getattr(django_settings, 'ODOO_UID', -1)
    db = getattr(django_settings, 'ODOO_DB', '')
    try:
        if uid < 1:
            common = xmlrpclib.ServerProxy('%s/xmlrpc/2/common' % url)
            uid = common.authenticate(db, username, password, {})
        models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % url)
    
        result = models.execute_kw(db, uid, password,
            'res.partner', 'direct_increase_by_customer_number',
            [],
            {'customer_number': customer_number, 
             'vals':{
                     'amount':amount,
                     'origin':origin,
                     'comment':comment,
                     }
             })
        return result
    except:
        return False


    