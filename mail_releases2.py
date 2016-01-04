###############################
'''
Created on 27 Feb 2012

@author: Kabelan-t
'''
##############################


import sys
import os
import os.path
import string
import random
import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#import maya.cmds as cmds
#import maya.mel as mel
import smtplib
from mpc.amandaClient.client import AmandaClient
from mpc.readPackageAPI.readPackage import *
from mpc.readPackageAPI.readCommon import *


job = os.environ['JOB']
shot = os.getenv("SHOT")
scene = os.getenv("SCENE")
user = os.environ['USER']

currentShot = shot.split("/")[-1:][0]


subject_str= ""
TO_str = ""
FROM_str = ""
CC_str=""

list1 = []
list2 = []
out_str = ""
body_text = ""


class publishEmail(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        
        self.setWindowTitle("Publish Email")
    
        self.mainLayout = QGridLayout()
        
        self.sendTo = job + '-3dreleases@moving-picture.com'
        #self.sendTo = 'kabelan-t@moving-picture.com'
        self.subject = job.upper()+ " : " + currentShot + str(' crowd released')
        self.from_str = user + '@moving-picture.com'
    
        self.label = QLabel("Email Releases ")
        self.label.setFont(QFont("Times", 16, QFont.Bold))
        self.T0_label = QLabel("To")
        self.TO_le = QLineEdit()
        self.TO_le.setText(self.sendTo)
        self.CC_label = QLabel("CC")
        self.CC_le = QLineEdit()
        
        self.CC_le.setText(job + '-prod@moving-picture.com' + '; ' + job+ '-lighting@moving-picture.com')
        self.subject_label = QLabel("Subject")
        self.subject_le = QLineEdit()
        self.subject_le.setText(self.subject)
        self.subject_le.setFont(QFont("Times", 12, QFont.Bold))
        self.body_te = QTextEdit()
        
        self.space_label = QLabel("")
        self.button_send = QPushButton("Send Email")
        
        self.mainLayout.addWidget(self.label, 1, 0)
        self.mainLayout.addWidget(self.T0_label, 2, 0)
        self.mainLayout.addWidget(self.TO_le, 2, 1)
        self.mainLayout.addWidget(self.CC_label, 3, 0)
        self.mainLayout.addWidget(self.CC_le, 3, 1)
        self.mainLayout.addWidget(self.subject_label, 4, 0)
        self.mainLayout.addWidget(self.subject_le, 4, 1)
        self.mainLayout.addWidget(self.body_te, 5, 1)
        self.mainLayout.addWidget(self.space_label, 6, 0)
        self.mainLayout.addWidget(self.button_send, 7, 1)
        self.mainLayout.addWidget(self.space_label, 8, 0)
        
        self.setLayout(self.mainLayout)
        self.resize(650, 780)
        
        
        QObject.connect(self.button_send, SIGNAL("clicked()"), self.clickButton)
        
        self.latestElements()
        self.printAll()
        
        self.message_begin = "Hi,\n\nPackages below are released and published. Please run latestAsset."
        self.message_end = "\n\nThanks\n"
        self.body_te.setText(self.message_begin + out_str + self.message_end + user)
                
        global subject_str
        subject_str = self.subject_le.displayText()
        global TO_str
        TO_str = self.sendTo
        global CC_str
        CC_str= self.CC_le.displayText()
        
            
           
    def clickButton(self):
        global TO_str
        global CC_str
        global subject_str
        TO_str = str(self.TO_le.displayText())
        CC_str = str(self.CC_le.displayText())
        subject_str = str(self.subject_le.displayText())
        #print TO_str
        CC_str = string.split(CC_str, '; ') 
    
        global body_text
        body_text = self.body_te.toPlainText()
        #print body_text
        
        self.sendMail()
        
             
    def sendMail(self):
        test_CClist = []
        SUBJECT = subject_str
        TO = TO_str
        FROM = self.from_str
        CC = CC_str
        text = str(body_text)
        #print text
        BODY = string.join((
                "From: %s" % FROM,
                "To: %s" % TO,
                "Subject: %s" % SUBJECT,
                "Cc: %s" % ";".join(CC),
                          
                text
                                                                  
                ), "\r\n")
                
        TO = [TO] + CC       
            
        try:
           smtpObj = smtplib.SMTP('localhost')
           smtpObj.sendmail(FROM, TO, BODY)         
           print "Successfully sent email"
        except smtplib.SMTPException:
           print "Error: unable to send email"
           
           
    def latestElements():
        bundles = AmandaClient.makeRequest("hub", "getReleasesBundles", job,  scene, currentShot)
        for bundle in bundles:
            if bundle == 'ShotPkg':
                print "\n"
                list1.append("\n")
                print bundle
                list1.append(bundle)
                elements = AmandaClient.makeRequest('hub','getReleasesElements', job , scene, currentShot , bundle)
                for element in elements:
                    if (element.startswith( 'anim' )):
                        latestVersion = AmandaClient.makeRequest('hub','getReleasesLatestVersion', job , scene, currentShot, bundle, element )
                        test1 = '%s -> v%s\n' % (element, latestVersion)
                        print test1
                        list1.append(test1)
                        shotPkg = ReadPackage(job=job, scene=scene, shot=currentShot, bundle=bundle, element=element, version=latestVersion)
                        layPkg = shotPkg["Layout"]["Cast"].value().object()
                        num = layPkg["Crowds"].numRows()
                        print "CrowdPkg (Inside ShotPkg)"
                        for row in range(0,num):
                            crowdPkg = layPkg["Crowds"][row]["Crowd"].value()
                            str_split = crowdPkg.toDotNotation().split('.', 5)
                            print '%s -> v%s' % (str_split[4], str_split[5])   
                        
                    
    def printAll(self):
        global out_str
        for l in list1:
            out_str += str(l)
            out_str += "\n"
            

app = QApplication(sys.argv)
widget = publishEmail()
widget.show()
app.exec_()





