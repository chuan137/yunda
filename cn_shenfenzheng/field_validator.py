# -*- coding: utf-8 -*-
from django.core import validators as field_validators
from django.core.exceptions import ValidationError
import re
from django.utils.translation import ugettext, ugettext_lazy as _

def field_validator_only_alphabeta_num(value):
    p = re.compile(u'^[a-zA-Z0-9\s\-\+\/\&,.()äÄöÖüÜ]+$')
    if not p.match(value):
        raise ValidationError(_('Only german/english alphabeta, numbers, and ",.-()+/&" allowed: %(value)s'), params={'value': value},)

def field_validator_only_chinese(value):
    p = re.compile(u'^[\s\u4e00-\u9fa5]+$')
    if not p.match(value):
        raise ValidationError(_('Only chinese allowed: %(value)s'), params={'value': value},)

def field_validator_chinese_and_alphabeta(value):
    p = re.compile(u'^[a-zA-Z0-9\s\-,.()\u4e00-\u9fa5]+$')
    if not p.match(value):
        raise ValidationError(_('Only chinese, alphabeta, number and "-,.()" allowed: %(value)s'), params={'value': value},)

def field_validator_chinese_mobile_phone(value):
    p = re.compile(u'^1[1-9][0-9]{9}$')
    if not p.match(value):
        raise ValidationError(_('Chinese mobile number wrong.pls without 0086 or +86: %(value)s'), params={'value': value},)

def field_validator_chinese_postcode(value):
    p = re.compile(u'^[0-9]{6}$')
    if not p.match(value):
        raise ValidationError(_('Chinese postcode should be 6 digits, not with 0 start: %(value)s'), params={'value': value},)

def field_validator_german_postcode(value):
    p = re.compile(u'^[0-9]{5}$')
    if not p.match(value):
        raise ValidationError(_('German postcode should be 5 digits: %(value)s'), params={'value': value},)
def field_validator_cn_shenfenzheng(value):
    p = re.compile("(^\d{15}$)|(^\d{17}([0-9]|X|x)$)")
    if not p.match(value):
        raise ValidationError(u"身份证号码错误")
