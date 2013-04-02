#This file is part account_parent_code module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL
from itertools import izip

__all__ = ['Account']


class Account(ModelSQL, ModelView):
    __name__ = 'account.account'

    @classmethod
    def __setup__(cls):
        super(Account, cls).__setup__()
        cls.parent.readonly = True
        cls._sql_constraints += [
            ('code_uniq', 'UNIQUE(code, company)', 'Account Code must be '
                'unique per company.'),
            ]

    @classmethod
    def _find_children(cls, id, code):
        if not code:
            return
        accounts = cls.search([
                ('id', '!=', id),
                ('code', 'ilike', '%s%%' % code),
                ('kind', '=', 'view'),
                ])
        to_update = []
        for account in accounts:
            if account.parent and account.parent.code is None:
                continue
            if not account.parent or len(account.parent.code) < len(code):
                to_update.append(account)
                continue
        domain = [
            ('id', '!=', id),
            ('code', 'ilike', '%s%%' % code),
            ]
        domain += [('code', 'not ilike', '%s%%' % x.code) for x in accounts]
        to_update += cls.search(domain)
        return to_update

    @classmethod
    def _find_parent(cls, code, invalid_ids=None):
        if not code:
            return
        if invalid_ids is None:
            invalid_ids = []
        # Set parent for current record
        accounts = cls.search([
                ('id', 'not in', invalid_ids),
                ('kind', '=', 'view')
                ])
        parent = None
        for account in accounts:
            if account.code is None:
                continue
            if code.startswith(account.code):
                if not parent or len(account.code) > len(parent.code):
                    parent = account
        return parent.id if parent else None

    @classmethod
    def create(cls, vlist):
        vlist = [x.copy() for x in vlist]
        for vals in vlist:
            code = vals.get('code')
            if code and 'parent' not in vals:
                vals['parent'] = cls._find_parent(code)
        accounts = super(Account, cls).create(vlist)
        for account, vals in izip(accounts, vlist):
            code = vals.get('code')
            if code and vals.get('kind') == 'view':
                to_update = cls._find_children(account.id, code)
                if to_update:
                    cls.write(to_update, {
                            'parent': account.id,
                            })
        return accounts

    @classmethod
    def write(cls, accounts, vals):
        if 'code' not in vals and 'kind' not in vals:
            super(Account, cls).write(accounts, vals)
            return
        for account in accounts:
            cls.write(account.childs, {
                    'parent': account.parent and account.parent.id,
                    })
            new_vals = vals.copy()
            if 'code' in vals and 'parent' not in vals:
                new_vals['parent'] = cls._find_parent(vals['code'],
                    invalid_ids=[account.id])
            super(Account, cls).write([account], new_vals)
            new_account = cls(account.id)
            if new_account.code and new_account.kind == 'view':
                to_update = cls._find_children(new_account.id, new_account.code)
                if to_update:
                    cls.write(to_update, {
                            'parent': new_account.id,
                            })

    @classmethod
    def delete(cls, accounts):
        for account in accounts:
            cls.write(account.childs, {
                    'parent': account.parent and account.parent.id,
                    })
        return super(Account, cls).delete(accounts)
