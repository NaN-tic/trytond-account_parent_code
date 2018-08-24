# This file is part account_parent_code module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.model import Unique
from trytond.pool import PoolMeta
from trytond.transaction import Transaction

__all__ = ['AccountTemplate', 'Account']


class AccountTemplate(metaclass=PoolMeta):
    __name__ = 'account.account.template'

    @classmethod
    def __setup__(cls):
        super(AccountTemplate, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints += [
            ('code_uniq', Unique(t, t.code, t.kind, t.type),
                'Account Code must be unique per kind.'),
            ]

    @classmethod
    def copy(cls, templates, default=None):
        if default is None:
            default = {}
        default = default.copy()

        if 'code' in default:
            return super(AccountTemplate, cls).copy(templates, default)

        new_templates = []
        for template in templates:
            if template.code:
                x = 0
                while True:
                    x += 1
                    code = '%s (%d)' % (template.code, x)
                    if not cls.search([('code', '=', code)]):
                        break
                default['code'] = code
            new_templates += super(AccountTemplate, cls).copy(
                [template], default=default)
        return new_templates


class Account(metaclass=PoolMeta):
    __name__ = 'account.account'

    @classmethod
    def __setup__(cls):
        super(Account, cls).__setup__()
        # Fields not allowed to modify in accounts created from templates
        cls._check_account_template = set(['code'])
        t = cls.__table__()
        cls.parent.readonly = True
        cls._sql_constraints += [
            ('code_uniq', Unique(t, t.code, t.company),
                'Account Code must be unique per company.'),
            ]
        cls._error_messages.update({
                'account_from_template': ('You can not modify/delete account '
                    '"%s" because it is created from an account template.'),
                })

    @classmethod
    def check_account_template(cls, accounts):
        'Check accounts from templates to prevent modifications/deletions.'
        for account in accounts:
            if account.template:
                cls.raise_user_error('account_from_template',
                    (account.rec_name,))

    @classmethod
    def _find_children(cls, id, code, company_id):
        if not code:
            return
        accounts = cls.search([
                ('company', '=', company_id),
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
            ('company', '=', company_id),
            ('id', '!=', id),
            ('code', 'ilike', '%s%%' % code),
            ]
        domain += [('code', 'not ilike', '%s%%' % x.code) for x in accounts]
        to_update += cls.search(domain)
        return to_update

    @classmethod
    def _find_parent(cls, code, company_id, invalid_ids=None):
        if not code:
            return
        if invalid_ids is None:
            invalid_ids = []
        domain = [
            ('id', 'not in', invalid_ids),
            ('kind', '=', 'view')
            ]
        if company_id:
            domain.append(('company', '=', company_id))
        # Set parent for current record
        accounts = cls.search(domain)
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
            company_id = vals.get('company_id',
                Transaction().context.get('company_id'))
            if code and 'parent' not in vals:
                vals['parent'] = cls._find_parent(code, company_id)
        accounts = super(Account, cls).create(vlist)
        for account, vals in zip(accounts, vlist):
            code = vals.get('code')
            if code and vals.get('kind') == 'view':
                to_update = cls._find_children(account.id, code,
                    account.company.id)
                if to_update:
                    cls.write(to_update, {
                            'parent': account.id,
                            })
        return accounts

    @classmethod
    def write(cls, *args):
        actions = iter(args)
        to_check = []
        for accounts, values in zip(actions, actions):
            if (not Transaction().context.get('update_from_template') and
                    set(values.keys()) & cls._check_account_template):
                cls.check_account_template(accounts)
            if 'code' in values or 'kind' in values:
                to_check += [accounts, values]
        super(Account, cls).write(*args)
        to_check = iter(to_check)
        for accounts, values in zip(to_check, to_check):
            for account in accounts:
                # No need to check them accounts with templates as it is not
                # possible to modify them, so we should trust template values
                if account.template:
                    continue
                if account.childs:
                    cls.write(list(account.childs), {
                            'parent': account.parent and account.parent.id,
                            })
                new_values = values.copy()
                if 'code' in values and 'parent' not in values:
                    new_values['parent'] = cls._find_parent(values['code'],
                        account.company.id, invalid_ids=[account.id])
                super(Account, cls).write([account], new_values)
                new_account = cls(account.id)
                if new_account.code and new_account.kind == 'view':
                    to_update = cls._find_children(new_account.id,
                        new_account.code, account.company.id)
                    if to_update:
                        cls.write(to_update, {
                                'parent': new_account.id,
                                })

    @classmethod
    def copy(cls, accounts, default=None):
        if default is None:
            default = {}
        default = default.copy()

        if 'code' in default:
            return super(Account, cls).copy(accounts, default)

        res = []
        for account in accounts:
            x = 0
            while True:
                x += 1
                code = '%s (%d)' % (account.code, x)
                if not cls.search([('code', '=', code)]):
                    break
            default['code'] = code
            res += super(Account, cls).copy([account], default)
        return res

    @classmethod
    def delete(cls, accounts):
        if (not Transaction().context.get('update_from_template')):
            cls.check_account_template(accounts)
        for account in accounts:
            cls.write(list(account.childs), {
                    'parent': account.parent and account.parent.id,
                    })
        return super(Account, cls).delete(accounts)

    def update_account(self, template2account=None, template2type=None):
        context = Transaction().context.copy()
        context['update_from_template'] = True
        with Transaction().set_context(context):
            return super(Account, self).update_account(
                template2account=template2account,
                template2type=template2type)
