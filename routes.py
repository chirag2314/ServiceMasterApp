from functools import wraps
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
@auth_required
def admin():
    user=Customer.query.get(session['user_id'])
    if not user.is_admin:
        flash('Unauthorized Access')
        session.pop('user_id', None)
        return redirect(url_for('login'))
    return render_template('admin.html', user=user, service=Service.query.all(), professional=Professional.query.all())


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
        return redirect(url_for('pprofile'))
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
        return redirect(url_for('cprofile'))

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
    name=request.form.get('name')
    if username == '' or password == '' or name == '':
        flash('fields cannot be empty.')
        return redirect(url_for('cregister'))
    if Customer.query.filter_by(username=username).first():
        flash('Username not available, please choose some other username')
        return redirect(url_for('cregister'))
    cuser=Customer(username=username, password=password, name=name)
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
    profile.save(file_path) #doubtful
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
@auth_required
def add_services():
    return render_template('services/addservice.html', user=Customer.query.get(session['user_id']))

@app.route('/services/addservice', methods=['POST'])
@auth_required
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
@auth_required
def edit_service(service_id):
    return render_template('services/editservice.html', service=Service.query.get(service_id))

@app.route('/services/<int:service_id>/edit', methods=['POST'])
@auth_required
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
@auth_required
def delete_service(service_id):
    return render_template('services/deleteservice.html', service=Service.query.get(service_id))

@app.route('/services/<int:service_id>/delete', methods=['POST'])
@auth_required
def delete_service_post(service_id):
    service=Service.query.get(service_id)
    if not service:
        flash('Service Does Not Exist')
        return redirect(url_for('admin'))
    db.session.delete(service)
    db.session.commit()
    flash('Service Deleted successfully')
    return redirect(url_for('admin'))