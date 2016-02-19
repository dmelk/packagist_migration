from pybitbucket.auth import *
from pybitbucket.bitbucket import *
import requests
import logging
import json
import sys
import getopt
import pickle

logging.captureWarnings(True)

help = "migrate.py -b <bitbucket user> -p <bitbucket password> -a <packagist url> -U <packagist user> -t <packagist api token> -n <team name>"

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

modera_repositories = Bitbucket(client=bitbucket).repositoryByTeam(username=team_name)
for repository in modera_repositories:
    names = repository['full_name'].split('/', 1)
    repository_name = names[1]
    if repository_name[:4] == 'xxx_' or repository_name in repositories:
        print 'skipping'
        continue
    repositories.append(repository_name)
    for clone_link in repository['links']['clone']:
        if clone_link['name'] == 'ssh':
            href = clone_link['href']
            r = requests.post(packagist_url+'api/create-package?username='+packagist_user+'&apiToken='+packagist_api_token, json={'repository': {'url': href}})
            try:
                resp = json.loads(packagist_url)
                if 'status' in resp and resp['status'] == 'ok':
                    print 'ok'
            except ValueError as e:
                pass
            break

out_file = open("repos.dump", "w")
pickle.dump(repositories, out_file)
out_file.close()