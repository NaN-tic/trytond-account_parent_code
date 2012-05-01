#!/usr/bin/env python
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

import sys
import os
DIR = os.path.abspath(os.path.normpath(os.path.join(__file__,
    '..', '..', '..', '..', '..', 'trytond')))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))

import unittest
import datetime
import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_view, test_depends
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction
from trytond.wizard import Session


class AccountParentCodeTestCase(unittest.TestCase):
    '''
    Test AccountParentCode module.
    '''

    def setUp(self):
        trytond.tests.test_tryton.install_module('account_parent_code')
        self.account_template = POOL.get('account.account.template')
        self.account = POOL.get('account.account')
        self.account_create_chart = POOL.get(
            'account.create_chart', type='wizard')
        self.company = POOL.get('company.company')
        self.user = POOL.get('res.user')
        self.fiscalyear = POOL.get('account.fiscalyear')
        self.sequence = POOL.get('ir.sequence')

#    def test0005views(self):
#        '''
#        Test views.
#        '''
#        test_view('account_parent_code')

    def test0006depends(self):
        '''
        Test depends.
        '''
        test_depends()

    def test0010account_chart(self):
        'Test creation of minimal chart of accounts'
        with Transaction().start(DB_NAME, USER,
                context=CONTEXT) as transaction:
            company_id, = self.company.search([('name', '=', 'B2CK')])
            self.user.write(USER, {
                    'main_company': company_id,
                    'company': company_id,
                    })
            root_id = self.account.create({
                    'name': 'root',
                    'code': '',
                    'kind': 'view',
                    'company': company_id,
                    })
            account_1_id = self.account.create({
                    'name': 'root',
                    'code': '1',
                    'kind': 'view',
                    'company': company_id,
                    })
            account_100_id = self.account.create({
                    'name': 'root',
                    'code': '100',
                    'kind': 'view',
                    'company': company_id,
                    })
            account_10_id = self.account.create({
                    'name': 'root',
                    'code': '10',
                    'kind': 'view',
                    'company': company_id,
                    })
            account_2_id = self.account.create({
                    'name': 'root',
                    'code': '2',
                    'kind': 'view',
                    'company': company_id,
                    })

            account_id, = self.account.search([('code', '=', '2')])
            account = self.account.browse(account_id)
            self.assertEqual(account.id, account_2_id)
            self.assertEqual(account.parent.id, root_id)

            account_id, = self.account.search([('code', '=', '100')])
            account = self.account.browse(account_id)
            self.assertEqual(account.id, account_100_id)
            self.assertEqual(account.parent.id, account_10_id)
            self.assertEqual(account.parent.parent.id, account_1_id)
            self.assertEqual(account.parent.parent.parent.id, root_id)

            #self.account.delete(account_10_id)
            #self.account.delete(account_1_id)
            account = self.account.browse(account_100_id)
            print "1: ", account_1_id
            print "10: ", account_10_id
            print "100: ", account_100_id
            print "ACC: ", account.parent
            self.assertEqual(account.parent.id, account_1_id)

#    def test0020account_chart(self):
#        'Test creation of minimal chart of accounts'
#        with Transaction().start(DB_NAME, USER,
#                context=CONTEXT) as transaction:
#            account_template_id, = self.account_template.search([
#                ('parent', '=', False),
#                ])
#            company_id, = self.company.search([('name', '=', 'B2CK')])
#            self.user.write(USER, {
#                    'main_company': company_id,
#                    'company': company_id,
#                    })
#            CONTEXT.update(self.user.get_preferences(context_only=True))
#
#            
#            session_id, _, _ = self.account_create_chart.create()
#            session = Session(self.account_create_chart, session_id)
#            session.data['account'].update({
#                    'account_template': account_template_id,
#                    'company': company_id,
#                    })
#            self.account_create_chart.transition_create_account(session)
#            receivable_id, = self.account.search([
#                    ('kind', '=', 'receivable'),
#                    ('company', '=', company_id),
#                    ])
#            payable_id, = self.account.search([
#                    ('kind', '=', 'payable'),
#                    ('company', '=', company_id),
#                    ])
#            session.data['properties'].update({
#                    'company': company_id,
#                    'account_receivable': receivable_id,
#                    'account_payable': payable_id,
#                    })
#            self.account_create_chart.transition_create_properties(
#                session)
#            transaction.cursor.commit()

def suite():
    suite = trytond.tests.test_tryton.suite()
    from trytond.modules.company.tests import test_company
    for test in test_company.suite():
        if test not in suite:
            suite.addTest(test)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountParentCodeTestCase))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
