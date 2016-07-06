# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response, redirect
from django.template.context import RequestContext
from django.core.context_processors import csrf
from cn_shenfenzheng import models, tasks
from cn_shenfenzheng.forms import CnShenfenzhengForm
from django.conf import settings
from PIL import Image, ImageFont, ImageDraw, ImageFile
import os
from django.http.response import HttpResponse
import json
import hashlib
import random
from django.core.urlresolvers import reverse
import logging
logger = logging.getLogger('django')

# Create your views here.
def get_img_from_idtmp(file_name):
    media_root = settings.MEDIA_URL
    base_dir = settings.BASE_DIR
    file_url = u"%sidtmp/%s" % (media_root, file_name)
    file_path = u"%s%s" % (base_dir, file_url)
    if not os.path.isfile(file_path): return False
    

def upload(request):
    get_data = request.GET
    prepage = False
    if get_data.has_key('prepage'):
        prepage = get_data['prepage'] or False
    c = dict()
    if request.method == 'POST':
        form = CnShenfenzhengForm(request.POST)        
        if form.is_valid():
            data = form.clean()
            file_name1 = data['shenfenzheng1']
            file_name2 = data['shenfenzheng2']
            media_root = settings.MEDIA_URL
            base_dir = settings.BASE_DIR
            sfz_tmp_dir = settings.SFZ_TMP_DIR_AT_MEDIA_ROOT        
            img1_path = u"%s%s%s%s" % (base_dir, media_root, sfz_tmp_dir, file_name1)
            img2_path = u"%s%s%s%s" % (base_dir, media_root, sfz_tmp_dir, file_name2)
            try:
                img1 = Image.open(img1_path)
                img2 = Image.open(img2_path)
                sfz_saved_path = image_merge([img1, img2], output_dir=settings.SFZ_ROOT_DIR, output_name=u'%s.jpg' % data['number'], restriction_max_width=800)                               
                sfz = form.save()
                
                redirect_to = reverse('cn_shenfenzheng_upload_success')
                if prepage:
                    redirect_to += "?prepage=" + prepage
                return redirect(redirect_to)
                
            except IOError as e:    
                redirect_to = reverse('cn_shenfenzheng_upload_fail')
                if prepage:
                    redirect_to += "?prepage=" + prepage
                return redirect(redirect_to)            
        
    else:
        
        c.update(csrf(request))
        form = CnShenfenzhengForm()
        c['form'] = form
        c['sfz_upload_url'] = getattr(settings, 'MAIN_ROOT_URL', 'http://yunda-express.eu') + reverse('cn_shenfenzheng_upload')
        return render_to_response('cn_shenfenzheng/upload.min.html', c, context_instance=RequestContext(request))
def upload_success(request):
    c = dict()
    return render_to_response('cn_shenfenzheng/success.html', c, context_instance=RequestContext(request))
def upload_fail(request):
    c = dict()
    return render_to_response('cn_shenfenzheng/fail.html', c, context_instance=RequestContext(request))
def preview(request):
    pass

def ajax_upload_image(request):
    if request.method == 'POST':
        sfz_root_dir = settings.SFZ_ROOT_DIR
        form = CnShenfenzhengForm(request.POST)       
        if form.is_valid():
            data = form.clean()
            number = data['number']
            mobile = data['mobile']
            name = data['name']
            obj, created = models.CnShenfengzheng.objects.get_or_create(name=name, number=number, mobile=mobile)
            if not created:
                return HttpResponse(json.dumps({'result':False, 'info':u'系统已经存在该身份证信息，无须再次提交'}), content_type="application/json")
            img = request.FILES['shenfenzheng'] or False
            if not img:
                return HttpResponse(json.dumps({'result':False, 'info':u'没有提交图片'}), content_type="application/json")
            try:
                parser = ImageFile.Parser()
                for chunk in img.chunks():
                    parser.feed(chunk)
                img = parser.close()
                
                img.save(sfz_root_dir + number + "-" + mobile + ".jpg", 'JPEG')
            except Exception as e:
                obj.delete()
                logger.error(e)
                return HttpResponse(json.dumps({'result':False, 'info':u"系统故障，暂时不能提交身份证"}), content_type="application/json")
            # tasks.cn_shenfenzheng_sync_to_erp.delay(obj)
            tasks.cn_shenfenzheng_sync_to_erp(obj)
            return HttpResponse(json.dumps({'result':True, 'info':u"身份证图片提交成功"}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'result':False, 'info':u"姓名、电话号码或身份证号码填写错误，请检查"}), content_type="application/json")
              

def ajax_upload(request):
    
    if request.method == 'POST':
        form = CnShenfenzhengForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.clean()
            media_root = settings.MEDIA_ROOT
            file_name = u"%s.jpg" % data['number']
            url = "%s%s" % (media_root, file_name)
            sfz, created = models.CnShenfengzheng.objects.get_or_create(name=data['name'], mobile=data['mobile'], number=data['number'])
            if created:                    
                zm = request.FILES['shenfenzheng1'] or False
                fm = request.FILES['shenfenzheng2'] or False
                if (not zm) or (not fm):
                    return HttpResponse(json.dumps({'result':False, 'info':u'没有提交图片'}), content_type="application/json")
                parser = ImageFile.Parser()
                for chunk in zm.chunks():
                    parser.feed(chunk)
                zm = parser.close()
                
                
                parser = ImageFile.Parser()
                for chunk in fm.chunks():
                    parser.feed(chunk)
                fm = parser.close()
                save_path = image_merge([zm, fm], "%s%s" % (settings.BASE_DIR, media_root), file_name, 1000, 1000, "%s%ssimsun.ttc" % (settings.BASE_DIR, media_root))
                sfz.shenfenzheng_url = url
                logger.debug(url)
                sfz.save()
            return HttpResponse(json.dumps({'result':True, 'info':url}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'result':False, 'info':u'输入错误'}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'result':False, 'info':u'输入错误'}), content_type="application/json")

def image_resize(img, size=(1000, 500)):
    try:  
        if img.mode not in ('L', 'RGB'):  
            img = img.convert('RGB')  
        img = img.resize(size)  
    except Exception, e:  
        pass  
    return img

def image_resize_with_max_width(img, max_width, max_height):
    try:  
        if img.mode not in ('L', 'RGB'):  
            img = img.convert('RGB')
        width, height = img.size
        w_ratio = float(width) / max_width
        h_ratio = float(height) / max_height
        
        ratio = (w_ratio >= h_ratio) and w_ratio or h_ratio
        if ratio >= 1:
            img = img.resize((int(width / ratio), int(height / ratio)))
    except Exception, e:  
        pass  
    return img

def image_merge(images, output_dir='output', output_name='merge.jpg', restriction_max_width=None, restriction_max_height=None):  
    """垂直合并多张图片 
    images - 要合并的图片路径列表 
    ouput_dir - 输出路径 
    output_name - 输出文件名 
    restriction_max_width - 限制合并后的图片最大宽度，如果超过将等比缩小 
    restriction_max_height - 限制合并后的图片最大高度，如果超过将等比缩小 
    """  
    max_width = 0  
    total_height = 0  
    # 计算合成后图片的宽度（以最宽的为准）和高度  
    for img in images:        
        width, height = img.size  
        if width > max_width:  
            max_width = width  
        total_height += height  
  
    # 产生一张空白图  
    new_img = Image.new('RGB', (max_width, total_height), (255, 255, 255))  
    # 合并  
    x = y = 0  
    for img in images:    
        width, height = img.size  
        new_img.paste(img, (x, y))  
        y += height  
  
    if restriction_max_width and max_width >= restriction_max_width:  
        # 如果宽带超过限制  
        # 等比例缩小  
        ratio = restriction_max_height / float(max_width)  
        max_width = restriction_max_width  
        total_height = int(total_height * ratio)  
        new_img = image_resize(new_img, size=(max_width, total_height))  
  
    if restriction_max_height and total_height >= restriction_max_height:  
        # 如果高度超过限制  
        # 等比例缩小  
        ratio = restriction_max_height / float(total_height)  
        max_width = int(max_width * ratio)  
        total_height = restriction_max_height  
        new_img = image_resize(new_img, size=(max_width, total_height))  
      
    if not os.path.exists(output_dir):  
        os.makedirs(output_dir)  
    save_path = '%s%s' % (output_dir, output_name)
    
    new_img.save(save_path, 'JPEG')  
    return save_path


