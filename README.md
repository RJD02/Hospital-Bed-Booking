# Hospital-Bed-Booking

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
