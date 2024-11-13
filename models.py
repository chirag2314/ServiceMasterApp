from flask_sqlalchemy import SQLAlchemy
from app import app
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy(app)

#Database Modelling

class Customer(db.Model):
    __tablename__='customer'
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(32), nullable=False, unique=True)
    passwordhash=db.Column(db.String(512), nullable=False)
    name=db.Column(db.String(64), nullable=False)
    pincode=db.Column(db.String(8), nullable=False)
    utype=db.Column(db.String(16), nullable=False, default='Customer')
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.passwordhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passwordhash, password)

class Professional(db.Model):
    __tablename__='professional'
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(32), nullable=False, unique=True)
    passwordhash=db.Column(db.String(512), nullable=False)
    name=db.Column(db.String(64), nullable=False)
    contact=db.Column(db.Integer, nullable=False)
    service_id=db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    experience=db.Column(db.Integer, nullable=False)
    pincode=db.Column(db.String(8), nullable=False)
    utype=db.Column(db.String(16), nullable=False, default='Professional')
    status=db.Column(db.String(16), nullable=True, default='Pending')
    profile=db.Column(db.String(512), nullable=False)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self,password):
        self.passwordhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passwordhash, password)

class Service(db.Model):
    __tablename__='service'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(32),nullable=False)
    price=db.Column(db.Integer, nullable=False)
    description=db.Column(db.String(512), nullable=False)
    time=db.Column(db.Integer,nullable=False)

    professionals=db.relationship('Professional', backref='service', lazy=True)

    def get_service_id(self, service):
        return id

class ServiceRequest(db.Model):
    __tablename__='servicerequests'
    servicereqid=db.Column(db.Integer,primary_key=True)
    cuser=db.Column(db.String(32),db.ForeignKey('customer.username'),nullable=False)
    puser=db.Column(db.String(32),db.ForeignKey('professional.username'),nullable=False)
    service_id=db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    requestdate=db.Column(db.DateTime, nullable=False)
    completedate=db.Column(db.DateTime, nullable=False)
    status=db.Column(db.String(32), nullable=False)
    rating=db.Column(db.String(32), nullable=False)
    review=db.Column(db.String(512), nullable=True)
    datetime=db.Column(db.DateTime,nullable=False)

    customers=db.relationship('Customer', backref='servicerequests', lazy=True)
    services=db.relationship('Service', backref='servicerequests', lazy=True)
    professionals=db.relationship('Professional', backref='servicerequests', lazy=True)

with app.app_context():
    db.create_all()
    cadmin = Customer.query.filter_by(username='admin').first()
    if not cadmin:
        admin=Customer(username='admin', password='admin', name='admin', pincode='000000', is_admin=True)
        db.session.add(admin)
        db.session.commit()