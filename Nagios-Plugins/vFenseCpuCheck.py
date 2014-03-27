import requests
import json
import cookielib
import optparse


api_version = '/api/v1'
api_call = '/reports/cpudetails'
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
opts, args = parser.parse_args()

manda = ['username','password','url']

def input():
    ''' Going to check the arguments else spit the help details '''
    for i in manda:
        if not opts.__dict__[i]:
            print "mandatory option username, password is missing\n"
            parser.print_help()
            exit(-1)


def nagiosCheck(node,idlePer,user,system):
    ''' This will Check the threshold status for all disk free space and create the alert '''

    if( idlePer > 20 ):
        print node + " Free CPU is OK :  "+str(idlePer)+"%"+" | "+str(user)+";"+str(system)+";"+str(idlePer)
    elif(idlePer <= 5 and idlePer >= 20):
        print node + " Free CPU is Warning :  "+str(idlePer)+"%"+" | "+str(user)+";"+str(system)+";"+str(idlePer)
    elif(idlePer <= 1 and idlePer >= 5):
        print node + " Free CPU is Critical :  "+str(idlePer)+"%"+" | "+str(user)+";"+str(system)+";"+str(idlePer)



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
    for key1,val1 in kk.items():
        if(key1=="data"):
            for i in val1:
                testMe.append(i)
    for i in testMe:
        nagiosCheck(i['computer-name'], i['idle'], i['user'], i['system'])


if __name__=='__main__':
    input()
    checkValue()