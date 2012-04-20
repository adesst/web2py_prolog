import html
STATUS_NOT_ACTIVE = 'N'

def html_custom_form(fieldname, form, **kwargs):
    custom = form.custom
    if kwargs.get('view',None):
        the_widget = custom.inpval[fieldname]
    else:
        the_widget = custom.widget[fieldname]
    result = '<td class="w2p_fl" %s> %s </td> \
        <td class="w2p_fc" %s> %s </td> \
        <td class="w2p_fw" %s> %s </td>' % ( kwargs.get('label_attributes',''),
            custom.label[fieldname], 
            kwargs.get('comment_attributes',''),
            custom.comment[fieldname], 
            kwargs.get('widget_attributes',''),
            the_widget)
    return html.XML(result,sanitize=False)
