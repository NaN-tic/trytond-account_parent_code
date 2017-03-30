# This file is part of the account_parent_code module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction


class AccountParentCodeTestCase(ModuleTestCase):
    'Test Account Parent Code module'
    module = 'account_parent_code'

    def setUp(self):
        super(AccountParentCodeTestCase, self).setUp()
        self.account_template = POOL.get('account.account.template')
        self.account = POOL.get('account.account')
        self.company = POOL.get('company.company')
        self.user = POOL.get('res.user')
        self.fiscalyear = POOL.get('account.fiscalyear')
        self.sequence = POOL.get('ir.sequence')

    def test0010parent_code(self):
        'Test parent code'
        with Transaction().start(DB_NAME, USER,
                context=CONTEXT):
            company, = self.company.search([
                    ('party.name', '=', 'Dunder Mifflin')])
            self.user.write([self.user(USER)], {
                    'main_company': company.id,
                    'company': company.id,
                    })

            # Account Template
            tpl_root, = self.account_template.create([{
                        'name': 'root',
                        'code': '',
                        'kind': 'view',
                        }])
            tpl_account_1, = self.account_template.create([{
                        'name': 'Account 1',
                        'code': '1',
                        'kind': 'view',
                        }])

            tpl_account_copy, = self.account_template.copy([tpl_account_1])
            self.assertEqual(tpl_account_copy.code, '1 (1)')
            tpl_account_copy2, = self.account_template.copy([tpl_account_1])
            self.assertEqual(tpl_account_copy2.code, '1 (2)')

            # Account
            root, = self.account.create([{
                        'name': 'root',
                        'code': '',
                        'kind': 'view',
                        'company': company.id,
                        }])
            account_1, = self.account.create([{
                        'name': 'Account 1',
                        'code': '1',
                        'kind': 'view',
                        'company': company.id,
                        }])
            account_100, = self.account.create([{
                        'name': 'Account 100',
                        'code': '100',
                        'kind': 'view',
                        'company': company.id,
                        }])
            account_10, = self.account.create([{
                        'name': 'Account 10',
                        'code': '10',
                        'kind': 'view',
                        'company': company.id,
                        }])
            account_2, = self.account.create([{
                        'name': 'Account 2',
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

            account_copy, = self.account.copy([account_1])
            self.assertEqual(account_copy.code, '1 (1)')
            account_copy2, = self.account.copy([account_1])
            self.assertEqual(account_copy2.code, '1 (2)')

def suite():
    suite = trytond.tests.test_tryton.suite()
    from trytond.modules.company.tests import test_company
    for test in test_company.suite():
        if test not in suite:
            suite.addTest(test)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountParentCodeTestCase))
    return suite
