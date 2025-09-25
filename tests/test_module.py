
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.


from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.modules.company.tests import (CompanyTestMixin, create_company,
    set_company)
from trytond.model.exceptions import SQLConstraintError


class AccountParentCodeTestCase(CompanyTestMixin, ModuleTestCase):
    'Test AccountParentCode module'
    module = 'account_parent_code'

    @with_transaction()
    def test_parent_code(self):
        'Test parent code'
        pool = Pool()

        TypeTemplate = pool.get('account.account.type.template')
        Type = pool.get('account.account.type')

        AccountTemplate = pool.get('account.account.template')
        Account = pool.get('account.account')
        Account = pool.get('account.account')

        company = create_company()
        with set_company(company):

            # Account Template
            tpl_root, = AccountTemplate.create([{
                        'name': 'root',
                        'code': '',
                        }])
            tpl_account_1, = AccountTemplate.create([{
                        'name': 'Account 1',
                        'code': '1',
                        'type': None,
                        }])

            tpl_account_copy, = AccountTemplate.copy([tpl_account_1])
            self.assertEqual(tpl_account_copy.code, '1 (1)')
            tpl_account_copy2, = AccountTemplate.copy([tpl_account_1])
            self.assertEqual(tpl_account_copy2.code, '1 (2)')

            # Type
            template_type_parent, = TypeTemplate.create([{
                        'name': 'Minimal Account Type Chart',
                        'statement': None,
                        }])
            template_type_asset, = TypeTemplate.create([{
                        'name': 'Asset',
                        'statement': 'balance',
                        'parent': template_type_parent,
                        }])
            type_parent, = Type.create([{
                        'name': 'Minimal Account Type Chart',
                        'statement': None,
                        }])
            type_asset, = Type.create([{
                        'name': 'Asset',
                        'statement': 'balance',
                        'parent': type_parent,
                        }])

            # Account
            root, = Account.create([{
                        'name': 'root',
                        'code': '',
                        'company': company.id,
                        }])
            account_1, = Account.create([{
                        'name': 'Account 1',
                        'code': '1',
                        'company': company.id,
                        }])
            account_100, = Account.create([{
                        'name': 'Account 100',
                        'code': '100',
                        'company': company.id,
                        }])
            account_10, = Account.create([{
                        'name': 'Account 10',
                        'code': '10',
                        'company': company.id,
                        }])
            account_2, = Account.create([{
                        'name': 'Account 2',
                        'code': '2',
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

            account_copy, = Account.copy([account_1])
            self.assertEqual(account_copy.code, '1 (1)')
            account_copy2, = Account.copy([account_1])
            self.assertEqual(account_copy2.code, '1 (2)')

            # raise SQL Constraint when create new accounts that code exists
            with self.assertRaises(SQLConstraintError):
                Account.create([{
                            'name': 'Account 1',
                            'code': '1',
                            'company': company.id,
                            }])

            Account.create([{
                        'name': 'Account 1',
                        'code': '1',
                        'type': type_asset,
                        }])
            with self.assertRaises(SQLConstraintError):
                Account.create([{
                            'name': 'Account 1',
                            'code': '1',
                            'type': type_asset,
                            }])

del ModuleTestCase
