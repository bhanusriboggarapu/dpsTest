#!/usr/bin/env python

import requests
import  json
import pytest
import subprocess
requests.packages.urllib3.disable_warnings()
getIdByName=pytest.helpers.getIdByName
getProtIp=pytest.helpers.getProtIp
findAndDelete=pytest.helpers.findAndDelete
null = None

#rest api from parameter file
# def pytest_generate_tests(metafunc):
#     if 'testdata' in metafunc.fixturenames:
#         with open("testdata.yml", 'r') as f:
#             Iterations = yaml.load(f)
#             metafunc.parametrize('testdata', [i for i in Iterations])




restReq=[
    ("post","/dps/v1/management/roles/",'{"name": "role1","description": "","mode": "MANUAL","allowall": False}',),
    ("post","/dps/v1/management/roles/",'{"name": "role2","description": "","mode": "MANUAL","allowall": False}',),
    ("post","/dps/v1/management/sources",'{"name":"FileSource1","description":"hkhjkh","type":"FILE","connection":{"userfile":"exampleusers.txt","groupfile":"examplegroups.txt"}}'),
    ("post",'/dps/v1/management/roles/{0}/members.getIdByName(login,"role1","roles")','[{"name":"exampleuser1","type":"USER","sourceid":getIdByName(login,"FileSource1","sources")}]'),
    ("post",'/dps/v1/management/roles/{0}/members.getIdByName(login,"role2","roles")','[{"name":"exampleuser2","type":"USER","sourceid":getIdByName(login,"FileSource1","sources")}]'),
    ("post","/dps/v1/management/dataelements/",'{"name": "DES","description": "Data Element with Triple DES protection, including IV, CRC and KID","type": "STRUCTURED","algorithm": "QID_3DES_CBC","ivtype": "SYSTEM_APPEND","checksumtype": "CRC32","cipherformat": "INSERT_KEYID_V1"}'),
    ('post', "/dps/v1/management/dataelements/",'{"name":"te_an","description":"DataElementwithalphanumerictokenization","type":"STRUCTURED","algorithm":"QID_TOKEN","tokenelement":{"type":"ALPHANUMERIC","tokenizer":"SLT_1_3","lengthpreserving":True,"fromleft":1,"fromright":3}}'),
    ('post', "/dps/v1/management/dataelements/",'{"name":"TE_CC_S13_L0R0","description":"TE_CC_S13_L0R0","type":"STRUCTURED","algorithm":"QID_TOKEN","tokenelement":{"type":"CREDITCARD","tokenizer":"SLT_1_3","fromleft":0,"fromright":0,"valueidentification":{	"invalidcardtype":False,	"invalidluhndigit":False,	"alphabeticindicator":False,	"alphabeticindicatorposition":1}}}'),
    ('post','/dps/v1/management/masks','{"name":"Mask_L2R2_Hash","description":"","fromleft":2,"fromright":2,"masked":True,"character":"#"}'),
    ('post','/dps/v1/management/policies/', '{"name": "Policy1","description": "","type": "STRUCTURED","permissions": {  "access": { "protect": True, "reprotect": False, "unprotect": True  },  "audit": { "success": {"protect": True,"reprotect": False,"unprotect": True }, "failed": {"protect": True,"reprotect": False,"unprotect": True }  }}}'),
    ('post','/dps/v1/management/policies/{0}/roles.getIdByName(login,"Policy1","policies")','[{"id":getIdByName(login,"role1","roles")},{"id":getIdByName(login,"role2","roles")}]'),
    ('post','/dps/v1/management/policies/{0}/dataelements.getIdByName(login,"Policy1","policies")','[{"id":getIdByName(login,"DES","dataelements")},{"id":getIdByName(login,"te_an","dataelements")}]'),
    ('post','/dps/v1/management/policies/{0}/roles/permissions.getIdByName(login,"Policy1","policies")','[{"id":getIdByName(login,"role1","roles"),"dataelements":[{"access":{"protect":True,"reprotect":True,"unprotect":True,"delete":True},"audit":{"success":{"protect":True,"reprotect":True,"unprotect":True,"delete":True},"failed":{"protect":True,"reprotect":True,"unprotect":True,"delete":True}},"maskid":0,"id":getIdByName(login,"te_an","dataelements")},{"access":{"protect":True,"reprotect":True,"unprotect":True,"delete":True},"audit":{"success":{"protect":True,"reprotect":True,"unprotect":True,"delete":True},"failed":{"protect":True,"reprotect":True,"unprotect":True,"delete":True}},"maskid":0,"id":getIdByName(login,"DES","dataelements")}]}]'),
    ('post','/dps/v1/management/policies/{0}/roles/permissions.getIdByName(login,"Policy1","policies")','[{"id":getIdByName(login,"role1","roles"),"dataelements":[{"access":{"protect":True,"reprotect":True,"unprotect":False,"delete":True},"audit":{"success":{"protect":True,"reprotect":True,"unprotect":True,"delete":True},"failed":{"protect":True,"reprotect":True,"unprotect":True,"delete":True}},"maskid":getIdByName(login,"Mask_L2R2_Hash","masks"),"id":getIdByName(login,"te_an","dataelements")},{"access":{"protect":True,"reprotect":True,"unprotect":True,"delete":True},"audit":{"success":{"protect":True,"reprotect":True,"unprotect":True,"delete":True},"failed":{"protect":True,"reprotect":True,"unprotect":True,"delete":True}},"noaccessoperation":"EXCEPTION","id":getIdByName(login,"DES","dataelements")}]}]'),
    ('post','/dps/v1/management/policies/{0}/ready.getIdByName(login,"Policy1","policies")','None'),
    ('post','/dps/v1/management/datastores','{"name": "Datastore1","description": "","default":False}'),
    ('post','/dps/v1/management/datastores/{0}/policies.getIdByName(login,"Datastore1","datastores")','[{"id": getIdByName(login,"Policy1","policies")}]'),
    ('post','/dps/v1/management/datastores/{0}/ranges.getIdByName(login,"Datastore1","datastores")','{"to":getProtIp(login),"from":getProtIp(login)}'),
    ('post','/dps/v1/management/datastores/{0}/deploy.getIdByName(login,"Datastore1","datastores")','None')
]
#testdata = [(line.rstrip('\n') ,) for line in open('inputAPI.param')]

def test_clear_esa(login):
    try:
        findAndDelete(login,'policies')
        findAndDelete(login,'datastores')
        findAndDelete(login,'dataelements')
        findAndDelete(login,'nodes')
    except:
        assert False




@pytest.mark.parametrize("type,api,payload",restReq)
#@pytest.mark.skipif(test='smoke',reason="skipping for now")
def test_setup_esa(type,api,payload,login):

    if "getIdByName" in api:

        uri,sub=api.split(".",1)
        sub = sub.split("&")
        ids=[]
        for i in sub:
            ids.append(eval(i))
        api=str(uri).format(*ids)
        ifmatch = pytest.helpers.getIfMatch(login, api, ids[0])
        login[1]['If-Match'] = ifmatch

    if type == "post":
        op = login[0].post('https://{0}{1}'.format(login[2],api), verify=False, data=json.dumps(eval(payload)),headers=login[1])
        if op.status_code==400:
            assert True

        else:
            assert op.status_code == 200


def test_protect(tools):
    xcApiTool=tools['xcApiTool']
    aa = subprocess.check_output(xcApiTool + ' -p 0 -u exampleuser1 -d1 DES -prot -in=raw -data jayant')
    print(aa.strip())