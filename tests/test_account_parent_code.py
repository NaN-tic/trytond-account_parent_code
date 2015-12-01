# This file is part of the account_parent_code module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class AccountParentCodeTestCase(ModuleTestCase):
    'Test Account Parent Code module'
    module = 'account_parent_code'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountParentCodeTestCase))
    return suite