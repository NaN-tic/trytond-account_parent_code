#This file is part account_parent_code module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from trytond.pool import Pool
from . import account


def register():
    Pool.register(
        account.AccountTemplate,
        account.Account,
        module='account_parent_code', type_='model')
