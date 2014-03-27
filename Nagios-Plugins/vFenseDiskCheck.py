import requests
import json
import cookielib
import optparse
import sys

api_version = '/api/v1'
api_call = '/reports/hardwaredetails'
login_uri = '/login'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
session = requests.session()
jar = cookielib.CookieJar()


parser = optparse.OptionParser()
parser.add_option('-U','--username', help='provide the username for authentication', dest='username',
    action='store')
parser.add_option('-P','--password', help='provice the password for authentication', dest='password',
    action='store')
parser.add_option('-u','--RVlink', help='provide the Remdiation Vault link', dest='url',
    action='store')
parser.add_option('-s','--disk-status', help='provide dist status like OK,WARNING,CRITICAL', dest='diskstatus',
    action='store')

opts, args = parser.parse_args()

manda = ['username','password','url','diskstatus']

fineState = []
warnState = []
critState = []


#status = { 'OK' : 0, 'WARNING' : 1, 'CRITICAL' : 2 , 'UNKNOWN' : 3}

def input():
    ''' Going to check the arguments else spit the help details '''
    for i in manda:
        if not opts.__dict__[i]:
            print "mandatory option username, password is missing\n"
            parser.print_help()
            exit(-1)
   

def nagiosCheck(arg1,arg2,arg3,arg4):
    ''' This will Check the threshold status for all disk free space and create the alert '''
    perCentVal = (int(arg1) * 100)/ int(arg4)    
    if(perCentVal > 30 ):
        fineState.append(str(arg3 +"  "+arg2 + "  Disk Free size is ok =  "+str(perCentVal)+"%"+" | "+str(arg3)+";"+str(arg2)+";"+str(arg1)+";"+str(arg4)+";"+str(perCentVal)))        
    elif(perCentVal <= 30 and perCentVal >= 10):
        warnState.append(str(arg3 +"  "+arg2 + "  Disk Free size is warning =  "+str(perCentVal)+"%"+" | "+str(arg3)+";"+str(arg2)+";"+str(arg1)+";"+str(arg4)+";"+str(perCentVal)))             
    elif(perCentVal <= 1 and perCentVal >= 10):
        critState.append(str(arg3 +"  "+arg2 + "  Disk Free size is critical =  "+str(perCentVal)+"%"+" | "+str(arg3)+";"+str(arg2)+";"+str(arg1)+";"+str(arg4)+";"+str(perCentVal)))


creds = {'username':opts.username , 'password': opts.password}


def checkValue():
    ''' will check the each disck status and call the nagios threshold check and update the status'''
    url = opts.url
    authenticated = session.post( url + login_uri, data=json.dumps(creds), verify=False, headers=headers, cookies=jar)
    if authenticated.ok:
        print 'authenticated'
        data = session.get( url + api_version + api_call, verify=False, headers=headers, cookies=jar)
        statusCode= data.status_code                
        if (statusCode == 200):
            kk =json.loads(data.content)
        else:
            print "There is a error in the API CALL"
            print "API Call Status Code is :" + str(statusCode)
            sys.exit(0)
    testMe = []
    perCentVal = 0
    for key1,val1 in kk.items():
        if(key1=="data"):
            for i in val1:
                testMe.append(i)
    for i in testMe:
        diskPart = len(i['disk'])
        if not (diskPart == 1):
            count = 0
            while (count < diskPart):
                nagiosCheck(i['disk'][count]['free_size_kb'], i['disk'][count]['name'], i['computer-name'],i['disk'][count]['size_kb'])
                count = count +1
        else:
            count = 0
            nagiosCheck(i['disk'][count]['free_size_kb'],i['disk'][count]['name'], i['computer-name'],i['disk'][count]['size_kb'],)

def declareAlerts():
    if (opts.diskstatus == "OK"):
        for i in fineState:
            print i
        sys.exit(0)   
    elif (opts.diskstatus == "WARNING"):
        if not (len(warnState)==0):
            for i in warnState:
                print i
            sys.exit(1)   
        else:
            print "There is no warning stage HDD usage in whole infra"
            sys.exit(0)
    elif (opts.diskstatus == "CRITICAL"):
        if not (len(critState)==0):
            for i in critState:
                print i
            sys.exit(2)   
        else:
            print "There is no critical stage HDD usage in whole infra"
            sys.exit(0)


if __name__=='__main__':
    input()
    checkValue()
    declareAlerts()
    
