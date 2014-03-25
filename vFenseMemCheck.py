import requests
import json
import cookielib
import optparse
import sys

api_version = '/api/v1'
api_call = '/reports/memorydetails'
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
parser.add_option('-s','--status', help='provide memory status like OK,WARNING,CRITICAL', dest='memorystatus',
    action='store')

opts, args = parser.parse_args()

manda = ['username','password','url','memorystatus']

fineState = []
warnState = []
critState = []


def input():
    ''' Going to check the arguments else spit the help details '''
    for i in manda:
        if not opts.__dict__[i]:
            print "mandatory option username, password is missing\n"
            parser.print_help()
            exit(-1)


def nagiosCheck(node,freePer,usedPer,freeMem,usedMem,total):
    ''' This will Check the threshold status for all disk free space and create the alert '''

    if(freePer > 20):
        fineState.append(str(node + " Free memory is OK :  "+str(freePer)+"%"+" | "+str(freeMem)+";"+str(usedMem)+";"+str(total)+";"+str(freePer)+";"+str(usedPer)))
    elif(freePer >= 5 and freePer <= 20):
        warnState.append(str(node + " Free memory is Warning :  "+str(freePer)+"%"+" | "+str(freeMem)+";"+str(usedMem)+";"+str(total)+";"+str(freePer)+";"+str(usedPer)))
    elif(freePer >= 1 and freePer <= 5):
        critState.append(str(node + " Free memory is Critical :  "+str(freePer)+"%"+" | "+str(freeMem)+";"+str(usedMem)+";"+str(total)+";"+str(freePer)+";"+str(usedPer)))


creds = {'username':opts.username , 'password': opts.password}

def checkValue():
    ''' will check the each disck status and call the nagios threshold check and update the status'''
    url = opts.url
    authenticated = session.post( url + login_uri, data=json.dumps(creds), verify=False, headers=headers, cookies=jar)
    if authenticated.ok:
        data = session.get( url + api_version + api_call, verify=False, headers=headers, cookies=jar)
        if data.ok:
            kk =json.loads(data.content)
    testMe = []
    for key1,val1 in kk.items():
        if(key1=="data"):
            for i in val1:
                testMe.append(i)
    for i in testMe:
        nagiosCheck(i['computer-name'],i['free-percent'], i['used-percentage'],i['free'], i['used'],i['total'])

def declareAlerts():
    if (opts.memorystatus == "OK"):
        for i in fineState:
            print i
        sys.exit(0)
    elif (opts.memorystatus == "WARNING"):
        if not (len(warnState)==0):
            for i in warnState:
                print i
            sys.exit(1)
        else:
            print "There is no warning stage HDD usage in whole infra"
            sys.exit(0)
    elif (opts.memorystatus == "CRITICAL"):
        if not (len(critState)==0):
            for i in critState:
                print i
            sys.exit(2)
        else:
            print "There is no critical stage memory usage in whole infra"
            sys.exit(0)


if __name__=='__main__':
    input()
    checkValue()
    declareAlerts()