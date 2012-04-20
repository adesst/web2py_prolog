from sqlhtml import FormWidget, StringWidget, TextWidget
from html import DIV, INPUT, FORM, LABEL, TEXTAREA

class StringWidget(StringWidget):
    _class = 'string'

    @classmethod
    def widget(cls, field, value, **attributes):
        """
        generates an INPUT text tag.

        see also: :meth:`FormWidget.widget`
        """

        default = dict(
            _type = 'text',
            _maxlength = field.length,
            value = (not value is None and str(value)) or '',
            )
        attr = cls._attributes(field, default, **attributes)

        return INPUT(**attr) 

class ModelIdWidget(FormWidget):
    _class = 'string'

    @classmethod
    def widget(cls, field, value, **attributes):
        """
        generates an INPUT text tag.

        see also: :meth:`FormWidget.widget`
        """
        import copy
        default = dict(
                _type = 'text',
                _size = 6,
                _class = 'string modelid_code',
                value = (not value is None and str(value)) or '',
            )
        attr = cls._attributes(field, default, **attributes)

        fake_field = copy.copy(field)
        fake_field.name = field.name+'_name' 
        record = attributes.get('record',None)
        if record:
            value = '%s' %record[fake_field.name] 
        default = dict(
                _type = 'text',
                _class = 'string modelid_name',
                value = (not value is None and str(value) ) or '',
            ) 
        attr2 = cls._attributes(fake_field, default, **attributes)
        attr2['requires'] = None
        return DIV(INPUT(**attr),INPUT(**attr2))

class TextWidget(TextWidget):
    _class = 'text'

    @classmethod
    def widget(cls, field, value, **attributes):
        """
        generates a TEXTAREA tag.

        see also: :meth:`FormWidget.widget`
        """
        # @TODO add length counter
        default = dict(value = value, _maxlength=field.length)
        attr = cls._attributes(field, default,
                               **attributes)
        return TEXTAREA(**attr)

class CodeNameWidget(FormWidget):
    _class = 'string'

    @classmethod
    def widget(cls, field, value, **attributes):
        """
        generates an INPUT text tag.

        see also: :meth:`FormWidget.widget`
        """
        import copy
        default = dict(
                _type = 'text',
                _size = 6,
                _class = 'string codename_code',
                value = (not value is None and str(value)) or '',
            )
        attr = cls._attributes(field, default, **attributes)

        fake_field = copy.copy(field)
        fake_field.name = field.name+'_name' 
        record = attributes.get('record',None)
        print record
        if record:
            value = '%s' %record[fake_field.name] 
        default = dict(
                _type = 'text',
                _class = 'string codename_name',
                value = (not value is None and str(value) ) or '',
            ) 
        attr2 = cls._attributes(fake_field, default, **attributes)
        attr2['requires'] = None
        return DIV(INPUT(**attr),INPUT(**attr2))
