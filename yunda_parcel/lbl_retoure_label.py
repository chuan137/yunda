# -*- coding: utf-8 -*-
import httplib#, urllib,urllib2
import lxml.etree as ET

class Dhl_Retoure():
    #static method
    @classmethod 
    def getLabel(self, firstname, lastname, street, streetNumber, postcode, city, customerReference, \
                 userName=u"weblobling", password=u"Lbl456123!", portalId="lobling", deliveryName="RetourenWeb02", \
                 host=u"amsel.dpwn.net", apiUrl=u"/abholportal/gw/lp/SoapConnector"):
        request = u"""<?xml version="1.0" encoding="iso-8859-1"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:var="https://amsel.dpwn.net/abholportal/gw/lp/schema/1.0/var3bl">
    <soapenv:Header>
        <wsse:Security soapenv:mustUnderstand="1" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
            <wsse:UsernameToken>
                <wsse:Username>%(userName)s</wsse:Username>
                <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">%(password)s</wsse:Password>
            </wsse:UsernameToken>
        </wsse:Security>
    </soapenv:Header>
    <soapenv:Body>
        <var:BookLabelRequest portalId ="%(portalId)s" deliveryName="%(deliveryName)s" shipmentReference="%(customerReference)s" customerReference="%(customerReference)s" labelFormat="PDF" senderName1="%(firstname)s" senderName2="%(lastname)s" senderCareOfName="" senderContactPhone="" senderStreet="%(street)s" senderStreetNumber="%(streetNumber)s" senderBoxNumber="" senderPostalCode="%(zip)s" senderCity="%(city)s"/>
    </soapenv:Body>
</soapenv:Envelope>"""
        try:
            request1=request % ({"firstname":firstname, "lastname":lastname, "street":street, "streetNumber":streetNumber,\
                                 "zip":postcode, "city":city, "customerReference":customerReference, \
                                 "userName":userName, "password":password, "portalId":portalId, "deliveryName":deliveryName})
            request=request1.encode('iso-8859-1')
            webservice = httplib.HTTPS(host)
            webservice.putrequest("POST", apiUrl)
            webservice.putheader("Host", host)
            webservice.putheader("User-Agent", "Python post")
            webservice.putheader("Content-type", "text/xml; charset=\"iso-8859-1\"")
            webservice.putheader("Content-length", "%d" % len(request))
            webservice.endheaders()
            webservice.send(request)
            statuscode, statusmessage, header = webservice.getreply()
            result = webservice.getfile().read()
#             print statuscode
#             print "----------------\n"
#             print statusmessage
#             print "----------------\n"
#             print header
#             print "----------------\n"
#             print result
            #xmlobj = base64.decodestring(task.xml_file).decode(task.xml_format).encode()
            xml = ET.fromstring(result)
            ns = {"var3bl":"https://amsel.dpwn.net/abholportal/gw/lp/schema/1.0/var3bl","env":"http://schemas.xmlsoap.org/soap/envelope/"}
            var3bl=xml.find("env:Body/var3bl:BookLabelResponse",namespaces=ns)
            if var3bl is None:
                raise Dhl_Retoure_Soap_Error(result)
                   
            attrib=var3bl.attrib
            pdf=var3bl.find("var3bl:label",namespaces=ns).text  
            
            return attrib, pdf
        except Dhl_Retoure_Soap_Error as e:
            return "",e.value
        except:
            return "","Unexpected error."

class Dhl_Retoure_Soap_Error(Exception):
    def __init__(self,value):
        self.value =value
    def __str__(self):
        return repr(self.value)
        

