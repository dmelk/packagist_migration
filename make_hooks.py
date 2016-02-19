from pybitbucket.auth import *
from pybitbucket.bitbucket import *
from pybitbucket.hook import *
import logging
import sys
import getopt
import pickle

logging.captureWarnings(True)

help = "make_hooks.py -b <bitbucket user> -p <bitbucket password> -a <packagist url> -U <packagist user> -t <packagist api token> -n <team name>"

hasOption = {'b': False, 'p': False, 'a': False, 'U': False, 't': False, 'n': False}

try:
    opts, args = getopt.getopt(sys.argv[1:], "hb:p:a:U:t:n:", ["bitbucket_user=", "bitbucket_pass=",
                                                                  "pacakgist_url=", "packagist_user",
                                                                  "packagist_api_token=", "team_name="])
except getopt.GetoptError:
    print help
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print help
        sys.exit()
    elif opt in ("-b", "--bitbucket_user"):
        hasOption['b'] = True
        bitbucket_user = arg
    elif opt in ("-p", "--bitbucket_pass"):
        hasOption['p'] = True
        bitbucket_pass = arg
    elif opt in ("-a", "--packagist_url"):
        hasOption['a'] = True
        packagist_url = arg
    elif opt in ("-U", "--packagist_user"):
        hasOption['U'] = True
        packagist_user = arg
    elif opt in ("-t", "--packagist_api_token"):
        hasOption['t'] = True
        packagist_api_token = arg
    elif opt in ("-n", "--team_name"):
        hasOption['n'] = True
        team_name = arg

for opt in hasOption:
    if not hasOption[opt]:
        print help
        sys.exit(2)

repositories = []
try:
    in_file = open("repos.dump", "r")
    repositories = pickle.load(in_file)
    in_file.close()
except IOError:
    pass

bitbucket = Client(
    BasicAuthenticator(
        bitbucket_user,
        bitbucket_pass,
        'pybitbucket@mailinator.com'))

for repository_name in repositories:
    Hook.create_hook(
        repository_name=repository_name,
        description='Hook for packagist',
        callback_url=packagist_url+'api/bitbucket?username='+packagist_user+'&apiToken='+packagist_api_token,
        active=True,
        events=['repo:push'],
        username=team_name,
        client=bitbucket
    )
