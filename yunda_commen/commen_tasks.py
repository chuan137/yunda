# -*- coding: utf-8 -*-
from celery import task
from django.core.mail import send_mail, get_connection
from django.contrib.auth.models import User
import logging
from yunda_user.models import DepositTransferNew
from xlwt.Workbook import Workbook
from decimal import Decimal
from parcel.models import IntlParcel
from yunda_parcel.models import DhlRetoureLabel
from django.core.mail.message import EmailMultiAlternatives
logger = logging.getLogger('django')

@task
def send_email(subject, content, to_emails=None, user_id=None, from_email=u'韵达德国分公司 <info@mail.yunda-express.eu>'):
    if not to_emails:
        to_emails=[]
    if user_id:
        user=User.objects.get(id=user_id)
        to_emails.append(user.email)
    try:
        send_mail(subject,
              "",
              from_email,
              to_emails,
              fail_silently=False,
              html_message=content)
    except Exception as e:
        logger.error("%s When send a mail" % e)
@task
def get_old_deposit_transfers_task():
    old_transfers = DepositTransferNew.objects.order_by("user", "-created_at")
    try:
        book = Workbook()
        chongzhi_sheet = book.add_sheet('ChongZhi')
        koukuan_sheet = book.add_sheet('KouKuan')
        chongzhi_row = 0
        koukuan_row = 0
        chongzhi_sheet.write(chongzhi_row, 0, u"客户编号")
        chongzhi_sheet.write(chongzhi_row, 1, u"金额")
        chongzhi_sheet.write(chongzhi_row, 2, u"单号")
        chongzhi_sheet.write(chongzhi_row, 3, u"描述")
        chongzhi_sheet.write(chongzhi_row, 4, u"时间")
        chongzhi_sheet.write(chongzhi_row, 5, u"货币")
        
        koukuan_sheet.write(koukuan_row, 0, u"客户编号")
        koukuan_sheet.write(koukuan_row, 1, u"金额")
        koukuan_sheet.write(koukuan_row, 2, u"单号")
        koukuan_sheet.write(koukuan_row, 3, u"描述")
        koukuan_sheet.write(koukuan_row, 4, u"时间")
        koukuan_sheet.write(koukuan_row, 5, u"货币")
        koukuan_sheet.write(koukuan_row, 6, u"已扣金额")
        koukuan_sheet.write(koukuan_row, 7, u"申报应付金额")
        koukuan_sheet.write(koukuan_row, 8, u"库房应付金额")
        koukuan_sheet.write(koukuan_row, 9, u"计费重量")
        koukuan_sheet.write(koukuan_row, 10, u"申报重量")
        koukuan_sheet.write(koukuan_row, 11, u"申报长度")
        koukuan_sheet.write(koukuan_row, 12, u"申报宽度")
        koukuan_sheet.write(koukuan_row, 13, u"申报高度")
        koukuan_sheet.write(koukuan_row, 14, u"库房重量")
        koukuan_sheet.write(koukuan_row, 15, u"库房长度")
        koukuan_sheet.write(koukuan_row, 16, u"库房宽度")
        koukuan_sheet.write(koukuan_row, 17, u"库房高度")
        chongzhi_row = 1
        koukuan_row = 1
        for old_transfer in old_transfers:
            if old_transfer.amount >= 0.01:
                chongzhi_sheet.write(chongzhi_row, 0, old_transfer.user.userprofile.customer_number)
                chongzhi_sheet.write(chongzhi_row, 1, round(Decimal(old_transfer.amount), 2))
                chongzhi_sheet.write(chongzhi_row, 2, old_transfer.origin)
                chongzhi_sheet.write(chongzhi_row, 3, old_transfer.ref)
                chongzhi_sheet.write(chongzhi_row, 4, old_transfer.created_at.strftime("%Y-%m-%d %H:%M:%S"))
                chongzhi_sheet.write(chongzhi_row, 5, old_transfer.user.userprofile.deposit_currency_type)
                chongzhi_row += 1
            else:
                koukuan_sheet.write(koukuan_row, 0, old_transfer.user.userprofile.customer_number)
                koukuan_sheet.write(koukuan_row, 1, round(Decimal(old_transfer.amount), 2))
                koukuan_sheet.write(koukuan_row, 2, old_transfer.origin)
                koukuan_sheet.write(koukuan_row, 3, old_transfer.ref)
                koukuan_sheet.write(koukuan_row, 4, old_transfer.created_at.strftime("%Y-%m-%d %H:%M:%S"))
                koukuan_sheet.write(koukuan_row, 5, old_transfer.user.userprofile.deposit_currency_type)
                try:
                    intl_parcel = IntlParcel.objects.get(yde_number=old_transfer.origin)
                    
                    koukuan_sheet.write(koukuan_row, 6, round(Decimal(intl_parcel.booked_fee or 0), 2))
                    #logger.error('axxx')
                    koukuan_sheet.write(koukuan_row, 7, round(Decimal(intl_parcel.get_fee() or 0), 2))  # u"申报应付金额")
                    #logger.error('bxxx')
                    try:
                        real_fee=intl_parcel.get_real_fee()
                    except:
                        real_fee=0
                    koukuan_sheet.write(koukuan_row, 8, round(Decimal(real_fee), 2))  # u"库房应付金额")
                    #logger.error('cxxx')
                    
                    vweight = intl_parcel.length_cm * intl_parcel.width_cm * intl_parcel.height_cm / 6000
                    real_vweight = intl_parcel.real_length_cm * intl_parcel.real_width_cm * intl_parcel.real_height_cm / 6000
                    chargeable_weight = max(w for w in [intl_parcel.weight_kg, vweight, intl_parcel.real_weight_kg, real_vweight])
                    #logger.error('dxxx')
                    koukuan_sheet.write(koukuan_row, 9, round(Decimal(chargeable_weight), 2))  # u"计费重量")
                    koukuan_sheet.write(koukuan_row, 10, round(Decimal(intl_parcel.weight_kg or 0), 2))  # u"申报重量")
                    koukuan_sheet.write(koukuan_row, 11, round(Decimal(intl_parcel.length_cm or 0), 2))  # u"申报长度")
                    koukuan_sheet.write(koukuan_row, 12, round(Decimal(intl_parcel.width_cm or 0), 2))  # u"申报宽度")
                    koukuan_sheet.write(koukuan_row, 13, round(Decimal(intl_parcel.height_cm or 0), 2))  # u"申报高度")
                    koukuan_sheet.write(koukuan_row, 14, round(Decimal(intl_parcel.real_weight_kg or 0), 2))  # u"库房重量")
                    koukuan_sheet.write(koukuan_row, 15, round(Decimal(intl_parcel.real_length_cm or 0), 2))  # u"库房长度")
                    koukuan_sheet.write(koukuan_row, 16, round(Decimal(intl_parcel.real_width_cm or 0), 2))  # u"库房宽度")
                    koukuan_sheet.write(koukuan_row, 17, round(Decimal(intl_parcel.real_height_cm or 0), 2))  # u"库房高度")
                      
                except IntlParcel.DoesNotExist:
                    try:
                        retoure = DhlRetoureLabel.objects.get(retoure_yde_number=old_transfer.origin)  
                        koukuan_sheet.write(koukuan_row, 6, "DHL Retoure")
                    except DhlRetoureLabel.DoesNotExist:
                        koukuan_sheet.write(koukuan_row, 6, "NOOOOOOOOOO")
                    except DhlRetoureLabel.MultipleObjectsReturned:
                        koukuan_sheet.write(koukuan_row, 6, "Retoure Duplicated")
                    except Exception as e:
                        logger.error(e)
                        koukuan_sheet.write(koukuan_row, 6, "%s" % e)
                except IntlParcel.MultipleObjectsReturned:
                    koukuan_sheet.write(koukuan_row, 6, "Intl Parcel Duplicated")
                except Exception as e:
                    logger.error(e)
                    logger.error(intl_parcel.yde_number)
                    koukuan_sheet.write(koukuan_row, 6, "%s" % e)
                koukuan_row += 1
                
        
        book.save("/tmp/old_transfers.xls")
        connection = get_connection(username=None,
                                    password=None,
                                    fail_silently=False)
        mail = EmailMultiAlternatives(u"Old deposit transfers", "", u'韵达德国分公司 <info@mail.yunda-express.eu>', ["lilee115@gmail.com"],
                                      connection=connection)
        mail.attach_file("/tmp/old_transfers.xls")
        mail.send()
        #return HttpResponse()
    except Exception as e:
        logger.error("%s" % e)
        #return HttpResponse(e)  
