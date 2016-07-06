#from celery import task
import logging
logger = logging.getLogger('sourceDns.webdns.async')
from django.conf import settings
import xmlrpclib
import base64



#@task
def cn_shenfenzheng_sync_to_erp(cn_shenfenzheng):
    
    cn_shenfenzheng.sync_status = 'waiting_to_sync'
    cn_shenfenzheng.save()
    
    # TODO sync 
    url = getattr(settings, 'ODOO_URL', 'localhost:8069')
    username = getattr(settings, 'ODOO_USERNAME', '')
    password = getattr(settings, 'ODOO_PASSWORD', '')
    db = getattr(settings, 'ODOO_DB', '')
    common = xmlrpclib.ServerProxy('%s/xmlrpc/2/common' % url)
    uid = common.authenticate(db, username, password, {})
    models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % url)
    
    sfz_root_dir = settings.SFZ_ROOT_DIR
    save_path = sfz_root_dir + cn_shenfenzheng.number + "-" + cn_shenfenzheng.mobile + ".jpg"
    
    try:
        with open(save_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read())
        id = models.execute_kw(db, uid, password, 'yunda2.shipment.cn.idcard', 'create', [{
            'idcard_number': cn_shenfenzheng.number,
            'cn_name':cn_shenfenzheng.name,
            'image_file':encoded_string,
            'cn_mobile':cn_shenfenzheng.mobile}])
        logger.debug('cn_shenfenzheng synced to erp')
        cn_shenfenzheng.sync_status = 'synced'
        cn_shenfenzheng.save()
    except Exception as e:
        logger.error(e)
        cn_shenfenzheng.sync_status = 'error'
        cn_shenfenzheng.save()
    
    return u'%s-%s.jpg synced to erp' % (cn_shenfenzheng.number, cn_shenfenzheng.mobile)



