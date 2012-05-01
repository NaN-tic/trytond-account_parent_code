#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import copy
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool


class AccountTemplate(ModelSQL, ModelView):
    _name = 'account.account.template'

    code = fields.Char('Code', size=None, select=True)
    parent = fields.Many2One('account.account.template', 'Parent', select=True,
            ondelete="RESTRICT")

#AccountTemplate()


class Account(ModelSQL, ModelView):
    _name = 'account.account'

    def __init__(self):
        super(Account, self).__init__()
        self.parent = copy.copy(self.parent)
        self.parent.readonly = True
        self._reset_columns()
        self._sql_constraints += [
            ('code_uniq', 'UNIQUE(code, company)', 'Account Code must be '
                'unique per company.'),
            ]

    def update_children(self, id, code):
        if not code:
            return
        # Set parent for children
        account_ids = self.search([
                ('id', '!=', id),
                ('code', 'ilike', '%s%%' % code),
                ('kind', '=', 'view'),
                ])
        accounts = self.browse(account_ids)
        ids_to_update = []
        for account in accounts:
            if account.parent and account.parent.code is None:
                continue
            if len(account.parent.code) < len(code):
                ids_to_update.append(account.id)
                continue
        prefixes = [x.code for x in accounts]
        domain = [
            ('id', '!=', id),
            ('code', 'ilike', '%s%%' % code), 
            ]
        domain += [('code', 'not ilike', '%s%%' % x) for x in prefixes]
        ids_to_update += self.search(domain)
        if ids_to_update:
            self.write(ids_to_update, {
                    'parent': id,
                    })

    def update_parent(self, code, invalid_ids=None):
        if not code:
            return
        if invalid_ids is None:
            invalid_ids = []
        # Set parent for current record
        ids = self.search([
                ('id', 'not in', invalid_ids),
                ('kind', '=', 'view')
                ])
        parent = None
        for account in self.browse(ids):
            if account.code is None:
                continue
            if code.startswith(account.code):
                if not parent or len(account.code) > len(parent.code):
                    parent = account
        return parent.id if parent else None

    def create(self, vals):
        code = vals.get('code')
        if code and 'parent' not in vals:
            vals = vals.copy()
            vals['parent'] = self.update_parent(code)
        id = super(Account, self).create(vals)
        if code and vals.get('kind') == 'view':
            self.update_children(id, code)
        return id

    #def write(self, ids, vals):
        #code = vals.get('code')
        #
        #if code and 'parent' not in vals:
            #if len(ids) > 1:
                #
        #res = super(Account, self).write(ids, vals)
        #return res

    def delete(self, ids):
        move_line_obj = Pool().get('account.move.line')
        if isinstance(ids, (int, long)):
            ids = [ids]
        account_ids = self.search([('parent', 'in', ids)])
        for account in self.browse(account_ids):
            parent_id = self.update_parent(account.code, [account.id] + ids)
            print "SETTING PARENT %s FOR %s" % (self.browse(parent_id).code, account.code)
            self.write(account.id, {
                    'parent': parent_id,
                    })
            print "WRITTEN"
        print "DELETING"
        return super(Account, self).delete(account_ids)

Account()


