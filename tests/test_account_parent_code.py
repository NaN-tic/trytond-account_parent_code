#!/usr/bin/env python
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_depends
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction


class AccountParentCodeTestCase(unittest.TestCase):
    '''
    Test AccountParentCode module.
    '''

    def setUp(self):
        trytond.tests.test_tryton.install_module('account_parent_code')
        self.account_template = POOL.get('account.account.template')
        self.account = POOL.get('account.account')
        self.company = POOL.get('company.company')
        self.user = POOL.get('res.user')
        self.fiscalyear = POOL.get('account.fiscalyear')
        self.sequence = POOL.get('ir.sequence')

    def test0006depends(self):
        '''
        Test depends.
        '''
        test_depends()

    def test0010account_chart(self):
        'Test creation of minimal chart of accounts'
        with Transaction().start(DB_NAME, USER,
                context=CONTEXT):
            company, = self.company.search([
                    ('party.name', '=', 'Dunder Mifflin')])
            self.user.write([self.user(USER)], {
                    'main_company': company.id,
                    'company': company.id,
                    })
            root, = self.account.create([{
                        'name': 'root',
                        'code': '',
                        'kind': 'view',
                        'company': company.id,
                        }])
            account_1, = self.account.create([{
                        'name': 'root',
                        'code': '1',
                        'kind': 'view',
                        'company': company.id,
                        }])
            account_100, = self.account.create([{
                        'name': 'root',
                        'code': '100',
                        'kind': 'view',
                        'company': company.id,
                        }])
            account_10, = self.account.create([{
                        'name': 'root',
                        'code': '10',
                        'kind': 'view',
                        'company': company.id,
                        }])
            account_2, = self.account.create([{
                        'name': 'root',
                        'code': '2',
                        'kind': 'view',
                        'company': company.id,
                        }])

            account, = self.account.search([('code', '=', '2')])
            self.assertEqual(account, account_2)
            self.assertEqual(account.parent, root)

            account, = self.account.search([('code', '=', '100')])
            self.assertEqual(account, account_100)
            self.assertEqual(account.parent, account_10)
            self.assertEqual(account.parent.parent, account_1)
            self.assertEqual(account.parent.parent.parent, root)

            self.account.delete([account_10])
            self.assertEqual(account_100.parent, account_1)

            self.account.write([account_1], {
                    'code': '20'
                    })
            self.assertEqual(account_100.parent, root)
            self.assertEqual(account_1.parent, account_2)

            self.account.delete([account_2])
            self.assertEqual(account_1.parent, root)
            self.account.delete([root])
            self.assertEqual(account_1.parent, None)
            self.assertEqual(account_100.parent, None)
            self.account.write([account_1], {
                    'code': '1',
                    })
            self.assertEqual(account_100.parent, account_1)
            self.account.delete([account_100])
            self.assertEqual(account_1.childs, ())
            self.account.delete([account_1])



def suite():
    suite = trytond.tests.test_tryton.suite()
    from trytond.modules.company.tests import test_company
    for test in test_company.suite():
        if test not in suite:
            suite.addTest(test)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountParentCodeTestCase))
    return suite
