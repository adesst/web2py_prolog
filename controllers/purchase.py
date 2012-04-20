import datetime

def index(): return 'Purchase Section'

def purchase_request_read(): 
    id = request.get_vars.get('id', None)
    purchase_request_id = request.get_vars.get('purchase_request_id', None)
    if id:
        pass
    elif purchase_request_id:
        record = db(db.purchase_request.id == purchase_request_id).select().first()
        form = SQLFORM(db.purchase_request, record)
        return dict(form=form)
    else:
        records = db(db.purchase_request.id > 0).select()
        return dict(records=records)

def purchase_request_create():
    form = SQLFORM(db.purchase_request)
    form.vars.created_date = datetime.datetime.today()
    if form.process().accepted:
        response.flash = T('Record added')
        redirect(URL('purchase_request_dtl_create',vars=dict(purchase_request_id=form.vars.id)))
    return form

def purchase_request_update():
    try:
        form = SQLFORM(db.purchase_request, request.get_vars.get('id',None))
        form.vars.created_date = datetime.datetime.today()
        if form.process().accepted:
            response.flash = T('Record Updated')
        return form
    except:
        session.flash = T('Error: id is Null') 
        redirect(URL('purchase_request_read'))

def purchase_request_delete():
    if db(db.purchase_request.id == request.get_vars.get('id',None)).delete():
        session.flash = T('Record deleted')
    else:
        session.flash = T('No record to delete')
    redirect(URL('purchase_request_read'))

def purchase_request_dtl_create():
    purchase_request_id = request.get_vars.get('purchase_request_id', None)
    if not purchase_request_id:
        return T('Error: Purchase request id is NULL')
    return dict(purchase_request_id=purchase_request_id)

def purchase_request_dtl_create_ajax():
    purchase_request_id = request.get_vars.get('purchase_request_id', None)
    if not purchase_request_id:
        response.flash = T('Error: Purchase request id is NULL')
        redirect(URL('purchase_request_read'))
    records = db(db.purchase_request_dtl.purchase_request_id == purchase_request_id).select(
                    db.purchase_request_dtl.ALL,
                    db.item.name,
                    left=db.item.on(db.item.id == db.purchase_request_dtl.item_id),
                    orderby=db.purchase_request_dtl.id
              )
    form = SQLFORM(db.purchase_request_dtl)
    form.vars.purchase_request_id = purchase_request_id
    if form.process().accepted:
        response.flash = T('Record added')
    return dict(form=form, purchase_request_id=purchase_request_id,records=records)

def purchase_request_dtl_read():
    id = request.get_vars.get('id', None)
    purchase_request_id = request.get_vars.get('purchase_request_id', None)
    if id:
        pass
    elif purchase_request_id:
        records = db(db.purchase_request_dtl.purchase_request_id == purchase_request_id).select(
                        db.purchase_request_dtl.ALL,
                        db.item.name,
                        left=db.item.on(db.item.id == db.purchase_request_dtl.item_id),
                        orderby=db.purchase_request_dtl.id
                  )
        return dict(records=records)
    else:
        pass

def purchase_request_dtl_update_ajax():
    id = request.get_vars.get('id',None)
    purchase_request_id = request.get_vars.get('purchase_request_id',None)
    if id:
        records = db(db.purchase_request_dtl.purchase_request_id == purchase_request_id).select(
                        db.purchase_request_dtl.ALL,
                        db.item.name,
                        left=db.item.on(db.item.id == db.purchase_request_dtl.item_id),
                        orderby=db.purchase_request_dtl.id
                  )
        record = db(db.purchase_request_dtl.id == id).select().first()
        form = SQLFORM(db.purchase_request_dtl, record)
        if form.process().accepted:
            session.flash = 'Record updated'
            redirect(URL('purchase_request_dtl_create_ajax', vars=dict(purchase_request_id=purchase_request_id)))
        return dict(form=form, purchase_request_id=purchase_request_id, records=records)
    else:
        redirect(URL('purchase_request_dtl_create',
                vars=dict(purchase_request_id=purchase_request_id)
            )
        )
