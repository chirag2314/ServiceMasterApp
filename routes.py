from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
import os

from models import db, Customer, Professional, Service, ServiceRequest

from app import app

type='C'


def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please Login')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return inner

def admin_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please Login')
            return redirect(url_for('login'))
        user=Customer.query.get(session['user_id'])
        if not user.is_admin:
            flash('Unauthorized Access')
            return redirect(url_for('cprofile'))
        return func(*args, **kwargs)
    return inner


@app.route('/')
@auth_required
def defaultpage():
    if type=='P':
        return render_template('defaultpage.html', user=Professional.query.get(session['user_id']))
    else:
        user=Customer.query.get(session['user_id'])
        if user.is_admin:
            return redirect(url_for('admin'))
        return render_template('defaultpage.html', user=Customer.query.get(session['user_id']))

@app.route('/admin')
@admin_required
def admin():
    user=Customer.query.get(session['user_id'])
    if not user.is_admin:
        flash('Unauthorized Access')
        session.pop('user_id', None)
        return redirect(url_for('login'))
    return render_template('admin.html', user=user, service=Service.query.all(), professional=Professional.query.all(), servreq=ServiceRequest.query.all())


@app.route('/cprofile')
@auth_required
def cprofile():
    user=Customer.query.get(session['user_id'])
    if user.is_admin:
        return redirect(url_for('admin'))
    else:
        return render_template('cprofile.html',  user=user)

@app.route('/cprofile', methods=['POST'])
@auth_required
def cprofile_post():
    user = Customer.query.get(session['user_id'])
    username=request.form.get('username')
    password=request.form.get('password')
    if username == '' or password == '':
        flash('Username of Password cannot be empty.')
        return redirect(url_for('cprofile'))
    if Customer.query.filter_by(username=username).first() and username != user.username:
        flash('User exists, Please choose another username')
        return redirect(url_for('cprofile'))       
    user.username = username
    user.password = password
    db.session.commit()
    flash('Details Updated successfully')
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/pprofile')
@auth_required
def pprofile():
    user=Professional.query.get(session['user_id'])
    return render_template('pprofile.html',  user=user)

@app.route('/pprofile', methods=['POST'])
@auth_required
def pprofile_post():
    user = Professional.query.get(session['user_id'])
    username=request.form.get('username')
    password=request.form.get('password')
    if username == '' or password == '':
        flash('Username of Password cannot be empty.')
        return redirect(url_for('pprofile'))
    if Professional.query.filter_by(username=username).first() and username != user.username:
        flash('User exists, Please choose another username')
        return redirect(url_for('pprofile'))       
    user.username = username
    user.password = password
    db.session.commit()
    flash('Details Updated successfully')
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    usertype=request.form.get('usertype')
    username=request.form.get('username')
    password=request.form.get('password')
    if usertype=='professional':
        if username == '' or password == '':
            flash('Username or Password cannot be empty.')
            return redirect(url_for('login'))
        puser = Professional.query.filter_by(username=username).first()
        if not puser:
            flash('Incorrect Username or Password.')
            return redirect(url_for('login'))
        if not puser.check_password(password):
            flash('Incorrect Username or Password.')
            return redirect(url_for('login'))
        session['user_id'] = puser.id
        type='P'
        return redirect(url_for('pdashboard'))
    if usertype=='customer':
        if username == '' or password == '':
            flash('Username or Password cannot be empty.')
            return redirect(url_for('login'))
        cuser = Customer.query.filter_by(username=username).first()
        if not cuser:
            flash('Incorrect Username or Password.')
            return redirect(url_for('login'))
        if not cuser.check_password(password):
            flash('Incorrect Username or Password.')
            return redirect(url_for('login'))
        session['user_id'] = cuser.id
        type='C'
        if cuser.is_admin:
            return redirect(url_for('admin'))
        return redirect(url_for('cdashboard'))

@app.route('/cregister')
def cregister():
    return render_template('cregister.html')

@app.route('/pregister')
def pregister():
    return render_template('pregister.html',service=Service.query.all())

@app.route('/cregister', methods=['POST'])
def cregister_post():
    username=request.form.get('username')
    password=request.form.get('password')
    pincode=request.form.get('pincode')
    name=request.form.get('name')
    if username == '' or password == '' or pincode == '' or name == '':
        flash('fields cannot be empty.')
        return redirect(url_for('cregister'))
    if Customer.query.filter_by(username=username).first():
        flash('Username not available, please choose some other username')
        return redirect(url_for('cregister'))
    cuser=Customer(username=username, password=password, pincode=pincode, name=name)
    db.session.add(cuser)
    db.session.commit()
    flash('Customer successfully Registered.')
    return redirect(url_for('login'))

@app.route('/pregister', methods=['POST'])
def pregister_post():
    username=request.form.get('username')
    password=request.form.get('password')
    name=request.form.get('name')
    contact=request.form.get('contact')
    service=request.form.get('service')
    experience=request.form.get('experience')
    pincode=request.form.get('pincode')
    profile=request.files['profile']
    if username == '' or password == '' or name == '' or contact == '' or service == '' or experience == '' or pincode == '':
        flash('fields cannot be empty.')
        return redirect(url_for('pregister'))
    if Professional.query.filter_by(username=username).first():
        flash('Username not available, please choose some other username')
        return redirect(url_for('pregister'))
    if not (profile and (profile.filename.endswith('.doc') or profile.filename.endswith('.docx') or profile.filename.endswith('.pdf'))):
        flash('Invalid file, please upload .pdf, .doc or .docx files only')
        return redirect(url_for('pregister'))
    file_path = os.path.join('uploads', profile.filename)
    profile.save(file_path)
    status='Pending'
    puser=Professional(username=username, password=password, name=name, contact=contact, service_id=service, experience=experience, pincode=pincode,status=status, profile=file_path)
    db.session.add(puser)
    db.session.commit()
    flash('Professional successfully Registered')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/services/addservice')
@admin_required
def add_services():
    return render_template('services/addservice.html', user=Customer.query.get(session['user_id']))

@app.route('/services/addservice', methods=['POST'])
@admin_required
def add_service_post():
    name=request.form.get('servicename')
    price=request.form.get('serviceprice')
    description=request.form.get('servicedescription')
    time=request.form.get('servicetime')
    if name == '' or price == '' or description == '' or time == '':
        flash('fields cannot be empty.')
        return redirect(url_for('add_services'))
    serv=Service(name=name,price=price,description=description,time=time)
    db.session.add(serv)
    db.session.commit()
    flash('Service Added Successfully')
    return redirect(url_for('admin'))


@app.route('/services/<int:service_id>/edit')
@admin_required
def edit_service(service_id):
    return render_template('services/editservice.html', service=Service.query.get(service_id))

@app.route('/services/<int:service_id>/edit', methods=['POST'])
@admin_required
def edit_service_post(service_id):
    service=Service.query.get(service_id)
    if not service:
        flash('Service Does Not Exist')
        return redirect(url_for('admin'))
    name=request.form.get('servicename')
    price=request.form.get('serviceprice')
    description=request.form.get('servicedescription')
    time=request.form.get('servicetime')
    if name == '' or price == '' or description == '' or time == '':
        flash('fields cannot be empty.')
        return redirect(url_for('edit_service'))
    service.name=name
    service.price=price
    service.description=description
    service.time=time
    db.session.commit()
    flash('Service Edited Successfully')
    return redirect(url_for('admin'))


@app.route('/services/<int:service_id>/delete')
@admin_required
def delete_service(service_id):
    return render_template('services/deleteservice.html', service=Service.query.get(service_id))

@app.route('/services/<int:service_id>/delete', methods=['POST'])
@admin_required
def delete_service_post(service_id):
    service=Service.query.get(service_id)
    if not service:
        flash('Service Does Not Exist')
        return redirect(url_for('admin'))
    db.session.delete(service)
    db.session.commit()
    flash('Service Deleted successfully')
    return redirect(url_for('admin'))


@app.route('/services/<int:professional_id>/updatestatus')
@admin_required
def update_professional(professional_id):
    return render_template('professionals/updatestatus.html', professional=Professional.query.get(professional_id))

@app.route('/services/<int:professional_id>/updatestatus', methods=['POST'])
@admin_required
def update_professional_post(professional_id):
    professional=Professional.query.get(professional_id)
    if not professional:
        flash('Professional does not exist')
        return redirect(url_for('admin'))
    status=request.form.get('status')
    professional.status=status
    db.session.commit()
    flash('Professional Status Updated Successfully')
    return redirect(url_for('admin'))

@app.route('/cdashboard')
@auth_required
def cdashboard():
    user=Customer.query.get(session['user_id'])
    pincode=user.pincode
    search=request.args.get('search')
    if not search:
        return render_template('cdashboard.html',user=user, services=Service.query.all(), professional=Professional.query.filter_by(status='Approved', pincode=pincode), servreq=ServiceRequest.query.filter_by(cuser=user.username))
    return render_template('cdashboard.html',user=user, services=Service.query.filter(Service.name.ilike('%' + search + '%')).all(), professional=Professional.query.filter_by(status='Approved', pincode=pincode), servreq=ServiceRequest.query.filter_by(cuser=user.username))

@app.route('/cservices/<int:service_id>', methods=['POST'])
@auth_required
def cservices(service_id):
    user=Customer.query.get(session['user_id'])
    pincode=user.pincode
    return render_template('cservice.html',user=user, services=Service.query.filter_by(id=service_id), professional=Professional.query.filter_by(status='Approved', pincode=pincode, service_id=service_id))

@app.route('/cservices/<int:service_id>/cbookaservice/<int:professional_id>')
@auth_required
def cbookaservice(service_id, professional_id):
    user=Customer.query.get(session['user_id'])
    return render_template('cbookaservice.html',user=user, services=Service.query.get(service_id), professional=Professional.query.get(professional_id))

@app.route('/cservices/<int:service_id>/cbookaservice/<int:professional_id>', methods=['POST'])
@auth_required
def cbookaservice_post(service_id, professional_id):
    user=Customer.query.get(session['user_id'])
    prof=Professional.query.get(professional_id)
    serv=Service.query.get(service_id)
    sr=ServiceRequest(cuser=user.username, puser=prof.username, service_id=serv.id,requestdate=datetime.today(),status='Requested')
    db.session.add(sr)
    db.session.commit()
    flash("Congrats, Booking Created")
    return redirect(url_for('cdashboard'))

@app.route('/pdashboard')
@auth_required
def pdashboard():
    user=Professional.query.get(session['user_id'])
    return render_template('pdashboard.html',user=user, servreq=ServiceRequest.query.filter_by(puser=user.username))

@app.route('/pdashboard/<int:servicereq_id>/peditservicerequest')
@auth_required
def peditservicerequest(servicereq_id):
    user=Professional.query.get(session['user_id'])
    return render_template('peditservicerequest.html',user=user, servreq=ServiceRequest.query.get(servicereq_id))

@app.route('/pdashboard/<int:servicereq_id>/peditservicerequest', methods=['POST'])
@auth_required
def peditservicerequest_post(servicereq_id):
    servr=ServiceRequest.query.get(servicereq_id)    
    if not servr:
        flash('Request does not exist')
        return redirect(url_for('pdashboard'))
    status=request.form.get('status')
    servr.status=status
    db.session.commit()
    flash('Request Status Updated Successfully')
    return redirect(url_for('pdashboard'))

@app.route('/cdashboard/<int:servicereq_id>/ccloseservice')
@auth_required
def close_service(servicereq_id):
    return render_template('ccloseservice.html',servreq=ServiceRequest.query.get(servicereq_id))


@app.route('/cdashboard/<int:servicereq_id>/ccloseservice', methods=['POST'])
@auth_required
def close_service_post(servicereq_id):
    servr=ServiceRequest.query.get(servicereq_id)
    rating=request.form.get('rating')
    review=request.form.get('review')
    servr.rating=rating
    servr.review=review
    servr.completedate=datetime.today()
    servr.status='Closed'
    db.session.commit()
    return redirect(url_for('cdashboard'))
