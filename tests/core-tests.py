import httpretty

import logging
import os
import sure                     # flake8: noqa
import sys
import textwrap
import unittest

paths = [
    '..',
]
for path in paths:
    sys.path.append(os.path.abspath(path))

import pyaci

logging.captureWarnings(True)

url = 'https://praveek6-bld.insieme.local:7000'


class MoTests(unittest.TestCase):
    def setUp(self):
        self.api = pyaci.Node(url)
        self.tree = self.api.mit

    def testPolUni(self):
        uni = self.tree.polUni()
        uni.Rn.should.equal('uni')
        uni.Dn.should.equal('uni')
        uni._url().should_not.be.different_of(
            url + '/api/mo/' + uni.Dn + '.xml'
        )

    def testFvTenant(self):
        tenant = self.tree.polUni().fvTenant('common')
        tenant.Rn.should.equal('tn-common')
        tenant.Dn.should.equal('uni/tn-common')
        tenant._url().should_not.be.different_of(
            url + '/api/mo/' + tenant.Dn + '.xml'
        )

    def testFvTenantOptionalArgs(self):
        tenant = self.tree.polUni().fvTenant('common', descr='Common tenant')
        tenant.Dn.should.equal('uni/tn-common')
        tenant.descr.should.equal('Common tenant')

    def testFvTenantFromKeywordArguments(self):
        tenant = self.tree.polUni().fvTenant(
            name='common', descr='Common tenant'
        )
        tenant.Dn.should.equal('uni/tn-common')
        tenant.descr.should.equal('Common tenant')

    def testUrl(self):
        mos = self.api.mit
        mos._url().should.equal(url + '/api/mo.xml')

    def testUniFromDn(self):
        uni = self.api.mit.FromDn('uni')
        uni.should.be.an(pyaci.core.Mo)
        uni.ClassName.should.equal('polUni')
        uni.Dn.should.equal('uni')

    def testTenantFromDn(self):
        tenant = self.api.mit.FromDn('uni/tn-common')
        tenant.should.be.an(pyaci.core.Mo)
        tenant.ClassName.should.equal('fvTenant')
        tenant.name.should.equal('common')
        tenant.Dn.should.equal('uni/tn-common')

    def testEpPFromDn(self):
        epp = self.api.mit.FromDn(
            'uni/epp/fv-[uni/tn-infra/ap-access/epg-default]'
        )
        epp.should.be.an(pyaci.core.Mo)
        epp.ClassName.should.equal('fvEpP')
        epp.epgPKey.should.equal('uni/tn-infra/ap-access/epg-default')
        epp.Dn.should.equal('uni/epp/fv-[uni/tn-infra/ap-access/epg-default]')

    def testJson(self):
        uni = self.tree.polUni()
        tenant = uni.fvTenant('mgmt')
        tenant.Json.should_not.be.different_of(textwrap.dedent('''\
        {
          "fvTenant": {
            "attributes": {
              "name": "mgmt"
            }
          }
        }'''))

        uni.Json.should_not.be.different_of(textwrap.dedent('''\
        {
          "polUni": {
            "children": [
              {
                "fvTenant": {
                  "attributes": {
                    "name": "mgmt"
                  }
                }
              }
            ]
          }
        }'''))

    def testJsonSetter(self):
        tenant = self.tree.polUni().fvTenant('common')
        tenant.Json = textwrap.dedent('''\
        {
          "fvTenant": {
            "attributes": {
              "name": "common",
              "descr": "Common tenant for sharing"
            }
          }
        }''')
        tenant.name.should.equal('common')
        tenant.descr.should.equal('Common tenant for sharing')

    def testJsonSetterTree(self):
        tree = textwrap.dedent('''\
        {
          "polUni": {
            "children": [
              {
                "fvTenant": {
                  "attributes": {
                    "name": "test"
                  },
                  "children": [
                    {
                      "fvBD": {
                        "attributes": {
                          "name": "lab"
                        },
                        "children": [
                          {
                            "fvRsCtx": {
                              "attributes": {
                                "tnFvCtxName": "infra"
                              }
                            }
                          }
                        ]
                      }
                    }
                  ]
                }
              }
            ]
          }
        }''')
        uni = self.tree.polUni()
        uni.Json = tree
        uni.Json.should_not.be.different_of(tree)

    def testXml(self):
        uni = self.tree.polUni()
        tenant = uni.fvTenant('mgmt')
        tenant.Xml.should_not.be.different_of('<fvTenant name="mgmt"/>\n')

        uni.Xml.should_not.be.different_of(textwrap.dedent('''\
        <polUni>
          <fvTenant name="mgmt"/>
        </polUni>
        '''))

    def testXmlSetter(self):
        tenant = self.tree.polUni().fvTenant('common')
        tenant.Xml = '<fvTenant name="common" descr="Common tenant"/>'
        tenant.name.should.equal('common')
        tenant.descr.should.equal('Common tenant')

    def testXmlSetterTree(self):
        uni = self.tree.polUni()
        tree = textwrap.dedent('''\
        <polUni>
          <fvTenant name="test">
            <fvBD name="lab">
              <fvRsCtx tnFvCtxName="infra"/>
            </fvBD>
          </fvTenant>
        </polUni>
        ''')
        uni.Xml = tree
        uni.Xml.should_not.be.different_of(tree)

    def testMoWithNoNamingProperties(self):
        uni = self.tree.polUni()
        uni.fvTenant('test').fvBD('lab').fvRsCtx().tnFvCtxName = 'infra'
        uni.Xml.should_not.be.different_of(textwrap.dedent('''\
        <polUni>
          <fvTenant name="test">
            <fvBD name="lab">
              <fvRsCtx tnFvCtxName="infra"/>
            </fvBD>
          </fvTenant>
        </polUni>
        '''))

    def testPropertySetter(self):
        tenant = self.tree.polUni().fvTenant('mgmt')
        tenant.descr.should.be(None)
        tenant.descr = 'Sample description'
        tenant.descr.should.equal('Sample description')
        tenant.Xml.should.equal(
            '<fvTenant name="mgmt" descr="Sample description"/>\n'
        )

    def testMoChaining(self):
        uni = self.tree.polUni()
        (uni.fvTenant('test').
         fvCtx('infra').Up().
         fvBD('lab').fvRsCtx(tnFvCtxName='infra').Up(2).
         fvBD('hr').fvRsCtx(tnFvCtxName='infra'))
        uni.Xml.should_not.be.different_of(textwrap.dedent('''\
        <polUni>
          <fvTenant name="test">
            <fvCtx name="infra"/>
            <fvBD name="hr">
              <fvRsCtx tnFvCtxName="infra"/>
            </fvBD>
            <fvBD name="lab">
              <fvRsCtx tnFvCtxName="infra"/>
            </fvBD>
          </fvTenant>
        </polUni>
        '''))


class LoginTests(unittest.TestCase):
    def setUp(self):
        self.login = pyaci.Node('https://localhost').methods.Login(
            'jsmith', 'secret'
        )

    def testCreation(self):
        self.login._url().should.equal('https://localhost/api/aaaLogin.xml')
        self.login.Xml.should.equal(
            '<aaaUser pwd="secret" name="jsmith"/>\n'
        )
        self.login.Json.should.equal(textwrap.dedent('''\
        {
          "aaaUser": {
            "attributes": {
              "name": "jsmith",
              "pwd": "secret"
            }
          }
        }'''))

    @httpretty.activate
    def testJsonPOST(self):
        httpretty.register_uri(httpretty.POST,
                               'https://localhost/api/aaaLogin.json')
        self.login.POST(format='json')
        (httpretty.last_request().method).should.equal('POST')
        (httpretty.last_request().path).should.equal('/api/aaaLogin.json')
        (httpretty.last_request().body).should.equal(self.login.Json)

    @httpretty.activate
    def testXmlPOST(self):
        httpretty.register_uri(httpretty.POST,
                               'https://localhost/api/aaaLogin.xml')

        self.login.POST(format='xml')
        (httpretty.last_request().method).should.equal('POST')
        (httpretty.last_request().path).should.equal('/api/aaaLogin.xml')
        (httpretty.last_request().body).should.equal(self.login.Xml)


class LoginRefreshTests(unittest.TestCase):
    def setUp(self):
        self.login = pyaci.Node('https://localhost').methods.LoginRefresh

    def testCreation(self):
        self.login._url().should.equal('https://localhost/api/aaaRefresh.xml')

    @httpretty.activate
    def testAaaUserJsonGET(self):
        httpretty.register_uri(httpretty.GET,
                               'https://localhost/api/aaaRefresh.json')
        self.login.GET(format='json')
        (httpretty.last_request().method).should.equal('GET')
        (httpretty.last_request().path).should.equal('/api/aaaRefresh.json')


class ResolveClassTests(unittest.TestCase):
    def setUp(self):
        self.resolve = pyaci.Node('https://localhost').methods.ResolveClass('fvTenant')

    def testCreation(self):
        self.resolve._url().should.equal('https://localhost/api/class/fvTenant.xml')

    @httpretty.activate
    def testJsonGET(self):
        httpretty.register_uri(httpretty.GET,
                               'https://localhost/api/class/fvTenant.json',
                               body=textwrap.dedent('''\
        {
          "imdata":[
            {
              "fvTenant":{
                "attributes":{
                  "childAction":"",
                  "descr":"Test",
                  "dn":"uni/tn-mgmt",
                  "lcOwn":"local",
                  "modTs":"2014-10-14T04:15:15.589+00:00",
                  "monPolDn":"uni/tn-common/monepg-default",
                  "name":"mgmt",
                  "ownerKey":"",
                  "ownerTag":"",
                  "status":"",
                  "uid":"0"
                }
              }
            }
          ],
          "totalCount":"1"
        }
                               '''))
        result = self.resolve.GET(format='json')
        (httpretty.last_request().method).should.equal('GET')
        (httpretty.last_request().path).should.equal('/api/class/fvTenant.json')
        result.shouldnt.be.empty
        tenant = result[0]
        tenant.name.should.equal('mgmt')


class MethodsTests(unittest.TestCase):
    def setUp(self):
        self.url = 'https://localhost'
        self.tree = pyaci.Node(self.url).mit

    @httpretty.activate
    def testMoJsonGET(self):
        httpretty.register_uri(httpretty.GET,
                               'https://localhost/api/mo/uni/tn-mgmt.json',
                               body=textwrap.dedent('''\
        {
          "imdata":[
            {
              "fvTenant":{
                "attributes":{
                  "childAction":"",
                  "descr":"Test",
                  "dn":"uni/tn-mgmt",
                  "lcOwn":"local",
                  "modTs":"2014-10-14T04:15:15.589+00:00",
                  "monPolDn":"uni/tn-common/monepg-default",
                  "name":"mgmt",
                  "ownerKey":"",
                  "ownerTag":"",
                  "status":"",
                  "uid":"0"
                }
              }
            }
          ],
          "totalCount":"1"
        }
                               '''))
        result = self.tree.polUni().fvTenant('mgmt').GET(format='json')
        (httpretty.last_request().method).should.equal('GET')
        (httpretty.last_request().path).should.equal(
            '/api/mo/uni/tn-mgmt.json'
        )

        result = result[0]
        result.should.be.a(pyaci.core.Mo)
        result.ClassName.should.equal('fvTenant')
        result.descr.should.equal('Test')

    @httpretty.activate
    def testMoXmlGET(self):
        httpretty.register_uri(httpretty.GET,
                               'https://localhost/api/mo/uni/tn-mgmt.xml',
                               body=textwrap.dedent('''\
        <?xml version="1.0" encoding="UTF-8"?>
        <imdata totalCount="1">
            <fvTenant childAction="" descr="Test" dn="uni/tn-mgmt"
                      lcOwn="local" modTs="2014-10-14T04:15:15.589+00:00"
                      monPolDn="uni/tn-common/monepg-default" name="mgmt"
                      ownerKey="" ownerTag="" status="" uid="0"/>
        </imdata>
                               '''))
        result = self.tree.polUni().fvTenant('mgmt').GET(format='xml')
        (httpretty.last_request().method).should.equal('GET')
        (httpretty.last_request().path).should.equal('/api/mo/uni/tn-mgmt.xml')

        result = result[0]
        result.should.be.a(pyaci.core.Mo)
        result.ClassName.should.equal('fvTenant')
        result.descr.should.equal('Test')

    @httpretty.activate
    def testMoXmlGETWithOptions(self):
        httpretty.register_uri(
            httpretty.GET,
            'https://localhost/api/mo/uni/tn-mgmt.xml?rsp-subtree=full&',
            body=textwrap.dedent('''\
        <?xml version="1.0" encoding="UTF-8"?>
        <imdata totalCount="1">
            <fvTenant childAction="" descr="Test" dn="uni/tn-mgmt"
                      lcOwn="local" modTs="2014-10-14T04:15:15.589+00:00"
                      monPolDn="uni/tn-common/monepg-default" name="mgmt"
                      ownerKey="" ownerTag="" status="" uid="0"/>
        </imdata>
                               '''))
        options = {'rsp-subtree': 'full'}
        result = self.tree.polUni().fvTenant('mgmt').GET(
            format='xml', **options
        )
        (httpretty.last_request().method).should.equal('GET')
        (httpretty.last_request().path).should_not.be.different_of(
            '/api/mo/uni/tn-mgmt.xml?rsp-subtree=full&'
        )

        result = result[0]
        result.should.be.a(pyaci.core.Mo)
        result.ClassName.should.equal('fvTenant')
        result.descr.should.equal('Test')

    @httpretty.activate
    def testMoJsonDELETE(self):
        httpretty.register_uri(httpretty.DELETE,
                               'https://localhost/api/mo/uni/tn-test.json')
        self.tree.polUni().fvTenant('test').DELETE(format='json')
        (httpretty.last_request().method).should.equal('DELETE')
        (httpretty.last_request().path).should.equal(
            '/api/mo/uni/tn-test.json'
        )

    @httpretty.activate
    def testMoXmlDELETE(self):
        httpretty.register_uri(httpretty.DELETE,
                               'https://localhost/api/mo/uni/tn-test.xml')
        self.tree.polUni().fvTenant('test').DELETE(format='xml')
        (httpretty.last_request().method).should.equal('DELETE')
        (httpretty.last_request().path).should.equal('/api/mo/uni/tn-test.xml')

    @httpretty.activate
    def testMoJsonPOST(self):
        httpretty.register_uri(httpretty.POST,
                               'https://localhost/api/mo/uni/tn-test.json')
        tenant = self.tree.polUni().fvTenant('test')
        tenant.POST(format='json')
        (httpretty.last_request().method).should.equal('POST')
        (httpretty.last_request().path).should.equal(
            '/api/mo/uni/tn-test.json'
        )
        (httpretty.last_request().body).should.equal(tenant.Json)

    @httpretty.activate
    def testMoXmlPOST(self):
        httpretty.register_uri(httpretty.POST,
                               'https://localhost/api/mo/uni/tn-test.xml')
        tenant = self.tree.polUni().fvTenant('test')
        tenant.POST(format='xml')
        (httpretty.last_request().method).should.equal('POST')
        (httpretty.last_request().path).should.equal('/api/mo/uni/tn-test.xml')
        (httpretty.last_request().body).should.equal(tenant.Xml)
