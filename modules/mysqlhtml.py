import re
from dal import Row
from sqlhtml import  *
from mywidgethtml import StringWidget, TextWidget
from html import DIV,INPUT, FORM, LABEL, SPAN, TAG, A
from storage import Storage

table_field = re.compile('[\w_]+\.[\w_]+')
widget_class = re.compile('^\w*')

class MYSQLFORM(SQLFORM):

    def __init__(
        self,
        table,
        record = None,
        deletable = False,
        linkto = None,
        upload = None,
        fields = None,
        labels = None,
        col3 = {},
        submit_button = 'Submit',
        delete_label = 'Check to delete',
        showid = True,
        readonly = False,
        comments = True,
        keepopts = [],
        ignore_rw = False,
        record_id = None,
        formstyle = 'table3cols',
        buttons = ['submit'],
        separator = ': ',
        **attributes
        ):
        """
        SQLFORM(db.table,
               record=None,
               fields=['name'],
               labels={'name': 'Your name'},
               linkto=URL(f='table/db/')
        """

        self.ignore_rw = ignore_rw
        self.formstyle = formstyle
        nbsp = XML('&nbsp;') # Firefox2 does not display fields with blanks
        FORM.__init__(self, *[], **attributes)
        ofields = fields
        keyed = hasattr(table,'_primarykey')

        # Widgets override
        self.widgets['string'] = StringWidget
        self.widgets['text'] = TextWidget

        # if no fields are provided, build it from the provided table
        # will only use writable or readable fields, unless forced to ignore
        if fields is None:
            fields = [f.name for f in table if (ignore_rw or f.writable or f.readable) and not f.compute]
        self.fields = fields

        # make sure we have an id
        if self.fields[0] != table.fields[0] and \
                isinstance(table,Table) and not keyed:
            self.fields.insert(0, table.fields[0])

        self.table = table

        # try to retrieve the indicated record using its id
        # otherwise ignore it
        if record and isinstance(record, (int, long, str, unicode)):
            if not str(record).isdigit():
                raise HTTP(404, "Object not found")
            record = table._db(table._id == record).select().first()
            if not record:
                raise HTTP(404, "Object not found")
        self.record = record

        self.record_id = record_id
        if keyed:
            self.record_id = dict([(k,record and str(record[k]) or None) \
                                       for k in table._primarykey])
        self.field_parent = {}
        xfields = []
        self.fields = fields
        self.custom = Storage()
        self.custom.dspval = Storage()
        self.custom.inpval = Storage()
        self.custom.label = Storage()
        self.custom.comment = Storage()
        self.custom.widget = Storage()
        self.custom.linkto = Storage()

        # default id field name
        self.id_field_name = table._id.name

        sep = separator or ''

        for fieldname in self.fields:
            if fieldname.find('.') >= 0:
                continue

            field = self.table[fieldname]
            comment = None

            if comments:
                comment = col3.get(fieldname, field.comment)
            if comment is None:
                comment = ''
            self.custom.comment[fieldname] = comment

            if not labels is None and fieldname in labels:
                label = labels[fieldname]
            else:
                label = field.label
            self.custom.label[fieldname] = label

            field_id = '%s_%s' % (table._tablename, fieldname)

            #label_is_required = SPAN(field.comment or '',_class="is_required") if field.notnull == True else ''

            label = LABEL(label, label and sep, _for=field_id,
                          _id=field_id+SQLFORM.ID_LABEL_SUFFIX)

            row_id = field_id+SQLFORM.ID_ROW_SUFFIX
            if field.type == 'id':
                self.custom.dspval.id = nbsp
                self.custom.inpval.id = ''
                widget = ''

                # store the id field name (for legacy databases)
                self.id_field_name = field.name

                if record:
                    if showid and field.name in record and field.readable:
                        v = record[field.name]
                        widget = SPAN(v, _id=field_id)
                        self.custom.dspval.id = str(v)
                        xfields.append((row_id,label, widget,comment))
                    self.record_id = str(record[field.name])
                self.custom.widget.id = widget
                continue

            self.readonly = readonly

            if readonly and not ignore_rw and not field.readable:
                continue

            if record:
                default = record[fieldname]
            else:
                default = field.default
                if isinstance(default,CALLABLETYPES):
                    default=default()

            cond = readonly or \
                (not ignore_rw and not field.writable and field.readable)

            if default and not cond:
                default = field.formatter(default)
            dspval = default
            inpval = default

            if cond:

                # ## if field.represent is available else
                # ## ignore blob and preview uploaded images
                # ## format everything else
                if field.represent:
                    inp = represent(field,default,record)
                elif field.type in ['blob']:
                    continue
                elif field.type == 'upload':
                    inp = UploadWidget.represent(field, default, upload)
                elif field.type == 'boolean':
                    inp = self.widgets.boolean.widget(field, default, _disabled=True)
                else:
                    inp = field.formatter(default)
            elif field.type == 'upload':
                if hasattr(field, 'widget') and field.widget:
                    inp = field.widget(field, default, upload)
                else:
                    inp = self.widgets.upload.widget(field, default, upload)
            elif hasattr(field, 'widget') and field.widget:
                inp = field.widget(field, default, record=record)
            elif field.type == 'boolean':
                inp = self.widgets.boolean.widget(field, default)
                if default:
                    inpval = 'checked'
                else:
                    inpval = ''
            elif OptionsWidget.has_options(field):
                if not field.requires.multiple:
                    inp = self.widgets.options.widget(field, default)
                else:
                    inp = self.widgets.multiple.widget(field, default)
                if fieldname in keepopts:
                    inpval = TAG[''](*inp.components)
            elif field.type.startswith('list:'):
                inp = self.widgets.list.widget(field,default)
            elif field.type == 'text':
                inp = self.widgets.text.widget(field, default)
            elif field.type == 'password':
                inp = self.widgets.password.widget(field, default)
                if self.record:
                    dspval = PasswordWidget.DEFAULT_PASSWORD_DISPLAY
                else:
                    dspval = ''
            elif field.type == 'blob':
                continue
            else:
                field_type = widget_class.match(str(field.type)).group()
                field_type = field_type in self.widgets and field_type or 'string'
                inp = self.widgets[field_type].widget(field, default, record=record)

            xfields.append((row_id,label,inp,comment))
            self.custom.dspval[fieldname] = dspval or nbsp
            self.custom.inpval[fieldname] = inpval or ''
            self.custom.widget[fieldname] = inp

        # if a record is provided and found, as is linkto
        # build a link
        if record and linkto:
            db = linkto.split('/')[-1]
            for (rtable, rfield) in table._referenced_by:
                if keyed:
                    rfld = table._db[rtable][rfield]
                    query = urllib.quote('%s.%s==%s' % (db,rfld,record[rfld.type[10:].split('.')[1]]))
                else:
                    query = urllib.quote('%s.%s==%s' % (db,table._db[rtable][rfield],record[self.id_field_name]))
                lname = olname = '%s.%s' % (rtable, rfield)
                if ofields and not olname in ofields:
                    continue
                if labels and lname in labels:
                    lname = labels[lname]
                widget = A(lname,
                           _class='reference',
                           _href='%s/%s?query=%s' % (linkto, rtable, query))
                xfields.append((olname.replace('.', '__')+SQLFORM.ID_ROW_SUFFIX,
                                '',widget,col3.get(olname,'')))
                self.custom.linkto[olname.replace('.', '__')] = widget
#                 </block>

        # when deletable, add delete? checkbox
        self.custom.deletable = ''
        if record and deletable:
            widget = INPUT(_type='checkbox',
                            _class='delete',
                            _id=self.FIELDKEY_DELETE_RECORD,
                            _name=self.FIELDNAME_REQUEST_DELETE,
                            )
            xfields.append((self.FIELDKEY_DELETE_RECORD+SQLFORM.ID_ROW_SUFFIX,
                            LABEL(
                                delete_label,separator,
                                _for=self.FIELDKEY_DELETE_RECORD,
                                _id=self.FIELDKEY_DELETE_RECORD+SQLFORM.ID_LABEL_SUFFIX),
                            widget,
                            col3.get(self.FIELDKEY_DELETE_RECORD, '')))
            self.custom.deletable = widget

        # when writable, add submit button
        self.custom.submit = ''
        if not readonly:
            if 'submit' in buttons:
                widget = self.custom.submit = INPUT(_type='submit',
                               _value=submit_button)
            elif buttons:
                widget = self.custom.submit = DIV(*buttons)
            if self.custom.submit:
                xfields.append(('submit_record' + SQLFORM.ID_ROW_SUFFIX,
                                '', widget, col3.get('submit_button', '')))

        # if a record is provided and found
        # make sure it's id is stored in the form
        if record:
            if not self['hidden']:
                self['hidden'] = {}
            if not keyed:
                self['hidden']['id'] = record[table._id.name]

        (begin, end) = self._xml()
        self.custom.begin = XML("<%s %s>" % (self.tag, begin))
        self.custom.end = XML("%s</%s>" % (end, self.tag))
        table = self.createform(xfields)
        self.components = [table]

class RecordCompact(object):

    result = None

    def __init__(self, parent_tablename, record):
        """
        Compact a returned row of record, e.g:
        
        { location: <Row...location data>, area: <Row.. area data>, _extra: 'area on...'}
        which location <Row...> is : {name: 'petojo', area : '22', id: 7}
        and area is : {name : 'Pluit'}
        
        to

        {name: 'petojo', area : '22', id: 7, area_n : 'Pluit'}

        Note: area_n is come from 'area' tablename + '_n'

        So if you have table location and poastal_code, as location as parent tablename then
        {..., poastal_code_n : 'Poastal code'}
        """
        if len(record) == 0:
            return None
        record_instances = {k:v for k,v in record.iteritems() if isinstance(v, Row)}
        if not record:
            """
            record already compacted
            """
            self.result = record
            return  None
        parent = record_instances.get(parent_tablename,None)
        if not parent:
            raise ValueError('record_instances is None')
        del record_instances[parent_tablename]
        pass
