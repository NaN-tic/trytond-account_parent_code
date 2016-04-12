# This file is part of the account_parent_code module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
from trytond.pool import Pool
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction

from trytond.modules.company.tests import create_company, set_company


class AccountParentCodeTestCase(ModuleTestCase):
    'Test Account Parent Code module'
    module = 'account_parent_code'

    @with_transaction()
    def test0010parent_code(self):
        'Test parent code'
        pool = Pool()
        Account = pool.get('account.account')

        company = create_company()
        with set_company(company):
            root, = Account.create([{
                        'name': 'root',
                        'code': '',
                        'kind': 'view',
                        'company': company.id,
                        }])
            account_1, = Account.create([{
                        'name': 'root',
                        'code': '1',
                        'kind': 'view',
                        'company': company.id,
                        }])
            account_100, = Account.create([{
                        'name': 'root',
                        'code': '100',
                        'kind': 'view',
                        'company': company.id,
                        }])
            account_10, = Account.create([{
                        'name': 'root',
                        'code': '10',
                        'kind': 'view',
                        'company': company.id,
                        }])
            account_2, = Account.create([{
                        'name': 'root',
                        'code': '2',
                        'kind': 'view',
                        'company': company.id,
                        }])

            account, = Account.search([('code', '=', '2')])
            self.assertEqual(account, account_2)
            self.assertEqual(account.parent, root)

            account, = Account.search([('code', '=', '100')])
            self.assertEqual(account, account_100)
            self.assertEqual(account.parent, account_10)
            self.assertEqual(account.parent.parent, account_1)
            self.assertEqual(account.parent.parent.parent, root)

            Account.delete([account_10])
            self.assertEqual(account_100.parent, account_1)

            Account.write([account_1], {
                    'code': '20'
                    })
            self.assertEqual(account_100.parent, root)
            self.assertEqual(account_1.parent, account_2)

            Account.delete([account_2])
            self.assertEqual(account_1.parent, root)
            Account.delete([root])
            self.assertEqual(account_1.parent, None)
            self.assertEqual(account_100.parent, None)
            Account.write([account_1], {
                    'code': '1',
                    })
            self.assertEqual(account_100.parent, account_1)
            Account.delete([account_100])
            self.assertEqual(account_1.childs, ())


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountParentCodeTestCase))
    return suite
