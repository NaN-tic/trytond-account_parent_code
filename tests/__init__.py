# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
try:
    from trytond.modules.account_parent_code.tests.test_account_parent_code import suite
except ImportError:
    from .test_account_parent_code import suite

__all__ = ['suite']
