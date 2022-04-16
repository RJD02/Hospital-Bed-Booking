#importing required modules for the project
from flask import Flask,json,redirect,render_template,flash,request
from flask.globals import request,session
from flask.helpers import url_for
import json
#the security is for encrypting and decrypting of password
from werkzeug.security import  generate_password_hash,check_password_hash   #this is used by us so that we can provide
#a particular password for login and check if the id and password matches or not
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user
from flask_mail import Mail
import pymysql
pymysql.install_as_MySQLdb()

#local server connection

local_server = True
app = Flask(__name__)
app.secret_key="190731"

#opening the json file
#in read mode
with open('config.json','r') as c:
    params = json.load(c)['params']


#setting mail for admin to authenticate the hospital and sent them the permit
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['admin-email'],
    MAIL_PASSWORD=params['admin-password']
)

mail = Mail(app)

#login manager to check the login sessions and logout sessions
#gives unique user access

login_manager = LoginManager(app)
login_manager.login_view = 'login'


#SQL database Xamp Server connection
#app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://username:password@localhost/databaseName"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/hospital"
db = SQLAlchemy(app)


#syntax from internet
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) or Hospitaluser.query.get(int(user_id))


class Test(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50))

#database queries for user login/sign-in details
class User(UserMixin,db.Model):
    def get_id(self):
        return (self.userid)
    #if we dont return the userid it gets over-ridden and we couldn't login
    userid = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),unique=True)
    email = db.Column(db.String(100),unique=True)
    #two users can have same passwords
    password = db.Column(db.String(1000))
    #password is kept so big because it is converted in hash which is a very long string so we have to give bigger size

#creating class for hospitaluser which is to added by the admin
class Hospitaluser(UserMixin,db.Model):
    def get_id(self):
        return (self.id)
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(100), unique=True)
    #hoscode is hospital code
    HosCode = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(1000))
    #password can be same for 2 different hospital


class Hospitaldata(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    HosCode = db.Column(db.String(100),unique=True)
    HosName = db.Column(db.String(200))
    normalbed = db.Column(db.Integer)
    icubed = db.Column(db.Integer)
    ventbed = db.Column(db.Integer)


#creating a class for booking the bed
class Bookingbed(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),unique=True)
    #email = db.Column(db.String(100), unique=True)
    bedtype = db.Column(db.String(50))
    HosCode = db.Column(db.String(100))
    medicalhistory = db.Column(db.String(100))
    pname = db.Column(db.String(100))
    pphone = db.Column(db.String(12))
    paddress = db.Column(db.String(100))
    page = db.Column(db.Integer)



#routes and function where we connect frontend with our program
@app.route("/")     #here we have to use the route, where we will visit and what should be displayed onto the screen
def home():
    return render_template("index.html")


#user signup route
@app.route("/usersignup")
def user_sign():
    return render_template("usersignup.html")


#user login route
@app.route("/userlogin")
def user_log():
    return render_template("userlogin.html")


#creating a signup function
@app.route('/signup',methods=['POST','GET'])    #methods to send a post request and to get request
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        #print(email,username,password)
        encryption = generate_password_hash(password)
        #check if the user is existing user or new user
        user = User.query.filter_by(username=username).first()
        user_email = User.query.filter_by(email=email).first()
        if user or user_email:
            flash("Email-Id or username already exists\nPlease try with a different one","warning")
            return render_template("usersignup.html")
        new_user = db.engine.execute(
            f"INSERT INTO `user` (`username`,`email`,`password`) VALUES ('{username}','{email}','{encryption}') ")
        #return ('USER ADDED')
        #once we sign-up we don't have to login again so we check the same crediantials as for login of user
        user1 = User.query.filter_by(username=username).first()
        if user1 and check_password_hash(user1.password, password):
            login_user(user1)
            flash("SignIn Success","success")
            try:
                return  render_template('index.html')
            except Exception as e:
                return f"Try Again\nError:- {e}"
    return render_template("usersignup.html")


#login check
@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=="POST":
        #email = request.form.get('email')
        username=request.form.get('username')
        password=request.form.get('password')
        user=User.query.filter_by(username=username).first()
        #user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","info")
            return render_template("index.html")
            #return "Success"
        else:
            #passing flash message if login failed
            flash("Invalid Credentials",'danger')
            #it will redirect us to this page
            return render_template("userlogin.html")
            #return "Fail"

    return render_template("userlogin.html")


#login check for hospital
@app.route('/hospitalLogin',methods=['POST','GET'])
def hospitalLogin():
    if request.method=="POST":
        HosCode=request.form.get('HosCode')
        password=request.form.get('password')
        hospital_user=Hospitaluser.query.filter_by(HosCode=HosCode).first()
        if hospital_user and check_password_hash(hospital_user.password,password):
            login_user(hospital_user)
            flash("Login Success","info")
            return render_template("index.html")
            #return "Success"
        else:
            #passing flash message if login failed
            flash("Invalid Credentials",'danger')
            #it will redirect us to this page
            return render_template("hospitalLogin.html")
            #return "Fail"

    return render_template("hospitalLogin.html")


#adminlogin check
@app.route('/admin',methods=['POST','GET'])
def admin():
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        if(username==params['user'] and password==params['password']):
            session['user']=username
            flash("Admin Signned In","info")
            return render_template("addHospitalUser.html")
        else:
            flash("Invalid Credentials","danger")

    return render_template("admin.html")


#log-out route
@app.route("/logout")
#for logging out first we need to be logged-in so we use login_required
@login_required
def logout():
    logout_user()       #inbuilt function in module to logout the user
    flash("Logout Successfully","success")
    return redirect(url_for('login'))



@login_manager.user_loader
def load_hospital(hospital_id):
    return Hospitaluser.query.get(int(hospital_id))













#creating a route to add the details of hospital
#only admin is allowed to give access to add the hospital
#hospital data i.e. avaiblity of bed is a different function and route
@app.route('/addHospitalUser',methods=['POST','GET'])
def hospitalUser():
    #only when admin is logged in the following conditions will work
    if('user' in session and session['user']==params['user']):
        if request.method == "POST":
            email = request.form.get('email')
            HosCode = request.form.get('HosCode')
            password = request.form.get('password')
            encpassword = generate_password_hash(password)
            HosCode = HosCode.upper()
            emailUser = Hospitaluser.query.filter_by(email=email).first()
            #user_HosCode = HospitalUser.query.filter_by(HosCode=HosCode).first()
            if emailUser:
                flash("Email or Hospital Code is already taken","warning")
                #return render_template("admin.html")
            db.engine.execute(
                f"INSERT INTO `hospitaluser` (`email`,`HosCode`,`password`) VALUES ('{email}','{HosCode}','{encpassword}') ")
            #sending the mail in which there are details to the hospital user
            mail.send_message("Welcome",sender=params['admin-email'],recipients=[email],body=f"Thanks for registering on our site\nFollowing are your unique credentials\nEmail Address:- {email}\nHospital Code:- {HosCode}\nPassword:- {password}\n\nDon't share your password with anyone\n\n\t\tThank You")

            flash("Mail Sent and Data Inserted","success")
            return render_template("addHospitalUser.html")
    else:
        flash("Login and TryAgain","warning")
        return redirect(url_for('admin'))


#database connection testing
@app.route("/test")
def test():
    try:
        #all the queries we get and it is stored so that we can print it and see what's required
        a = Test.query.all()
        print(a)
        return "db connected"
    except Exception as e:
        #to get the exception we return e
        return f"db not connected {e}"

#admin logout route
@app.route('/logoutadmin')
def logoutadmin():
    session.pop('user')
    flash("Logged Out","success")
    #return redirect(url_for('home'))
    return redirect(url_for('admin'))

#route to enter hospital data
@app.route("/addHospitalInfo",methods=['POST','GET'])
def addHospitalInfo():
    #we check if the hospital code exists or not in the database
    #hc = current_user.HosCode
    email = current_user.email
    posts = Hospitaluser.query.filter_by(email=email).first()
    code = posts.HosCode
    #print(code)
    postsdata=Hospitaldata.query.filter_by(HosCode=code).first()
    if request.method == "POST":
        HosCode = request.form.get('HosCode')
        HosName = request.form.get('HosName')
        normalbed = request.form.get('normalBed')
        icubed = request.form.get('icuBed')
        ventbed = request.form.get('ventBed')
        HosCode = HosCode.upper()
        #if the hospital code is registered then only info can be added
        huser = Hospitaluser.query.filter_by(HosCode=HosCode).first()
        #if the hospital has previously entered data then we should update it
        hduser = Hospitaldata.query.filter_by(HosCode=HosCode).first()
        if hduser:
            flash("Data is already present you can update it","primary")
            return render_template('hospitaldata.html')
        if huser:
            db.engine.execute(f"INSERT INTO `hospitaldata` (`HosCode`,`HosName`,`normalbed`,`icubed`,`ventbed`) VALUES ('{HosCode}', '{HosName}','{normalbed}','{icubed}','{ventbed}')")
            flash("Data Inserted Successfully",'success')
        else:
            flash("Hospital Code Not Registered",'warning')
    return  render_template('hospitaldata.html',postsdata=postsdata)

#edit or update the hospital data
@app.route("/hedit/<string:id>",methods=['POST','GET'])
@login_required
#hedit is hospital edit
def hedit(id):
    posts = Hospitaldata.query.filter_by(id=id).first()

    if request.method == "POST":
        HosCode = request.form.get('Hoscode')
        HosName = request.form.get('HosName')
        normalbed = request.form.get('normalBed')
        icubed = request.form.get('icuBed')
        ventbed = request.form.get('ventBed')
        #HosCode = HosCode.upper()
        db.engine.execute(
            f"UPDATE `hospitaldata` SET `HosCode` ='{HosCode}',`HosName`='{HosName}',`normalbed`='{normalbed}',`icubed`='{icubed}',`ventbed`='{ventbed}' WHERE `hospitaldata`.`id`={id}")
        flash("Data Updated", "success")
        #return render_template("hospitalData.html")
        #return redirect("/")
        return redirect("/addHospitalInfo")


    posts=Hospitaldata.query.filter_by(id=id).first()
    return render_template("hedit.html", posts=posts)

#deleting the data
@app.route("/hdelete/<string:id>",methods=['POST','GET'])
@login_required
def hdelete(id):
    db.engine.execute(f"DELETE  FROM `hospitaldata` WHERE `hospitaldata`.`id` = '{id}'")
    db.engine.execute(f"DELETE  FROM `hospitaldata` WHERE `hospitaldata`.`id` = 'None'")
    flash("Data Deleted Successfully",'warning')
    return redirect('/addHospitalInfo')

#app route for patient details
#only get request as we want to get the data from the page
@app.route("/pdetails", methods=['GET'])
@login_required
def pdetails():
    code = current_user.username
    #print(code)
    data = Bookingbed.query.filter_by(username=code).first()

    return render_template("pdetails.html", data=data)


#route to book bed
@app.route('/bedbooking',methods=['POST','GET'])
@login_required
def bedbooking():
    query=db.engine.execute(f"SELECT * FROM `hospitaldata`")
    if request.method == "POST":
        username=request.form.get('username')
        #email = request.form.get('email')
        HosCode = request.form.get('HosCode')
        bedtype = request.form.get('bedtype')
        medicalhistory = request.form.get('medicalhistory')
        pname = request.form.get('pname')
        pphone = request.form.get('pphone')
        paddress = request.form.get('paddress')
        page = request.form.get('page')
        check = Hospitaldata.query.filter_by(HosCode=HosCode).first()
        if not check:
            flash("Hospital Code doesn't exists","warning")
        #we have to select particular data from the table where we have to select the particular bed so we use the hoscode as it is unique
        code = HosCode
        dbb = db.engine.execute(f"SELECT * FROM `hospitaldata` WHERE `hospitaldata`.`HosCode` = '{code}'")
        #selecting which bedtype is required to user
        bedtype = bedtype
        if bedtype=="NormalBed":
            for d in dbb:
                seat = d.normalbed
                #print(seat)
                ar = Hospitaldata.query.filter_by(HosCode=HosCode).first()
                ar.normalbed = seat-1
                db.session.commit()
        elif bedtype=="IcuBed":
            for d in dbb:
                seat = d.icubed
                #print(seat)
                ar = Hospitaldata.query.filter_by(HosCode=HosCode).first()
                ar.icubed=seat-1
                db.session.commit()

        elif bedtype=="VentBed":
            for d in dbb:
                seat = d.ventbed
                #print(seat)
                ar = Hospitaldata.query.filter_by(HosCode=HosCode).first()
                ar.ventbed = seat-1
                db.session.commit()
        else:
            pass
        check2 = Hospitaldata.query.filter_by(HosCode=HosCode).first()
        if(seat>0 and check2):
            res = Bookingbed(email=email,bedtype=bedtype,HosCode=HosCode,medicalhistory=medicalhistory,pname=pname,pphone=pphone,paddress=paddress,page=page)
            db.session.add(res)
            db.session.commit()
            flash("Bed Booked, Contact Hospital for further details","success")
        else:
            flash("Something went wrong, TRY AGAIN","danger")

    return render_template("booking.html",query=query)


#log-out for hospital route
@app.route("/hospitalLogout")
#for logging out first we need to be logged-in so we use login_required
@login_required
def hospital_logout():
    logout_user()       #inbuilt function in module to logout the user
    flash("Logout Successfully","success")
    #return "Logout Success"
    return render_template("hospitalLogin.html")




# @app.route("/1")
# def test1():
#     em = current_user.email
#     return current_user.email


#testing if the created template of html file works properly
# @app.route("/2")
# def test_temp():
#     try:
#         return render_template("xyz.html")
#     except Exception as e:
#         return e



if __name__ == '__main__':
    app.run(debug=True)  # to run the flask app