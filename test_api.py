import urllib.request
import json

try:
    req = urllib.request.urlopen('http://localhost:8000/api/v1/workspaces')
    data = req.read()
    with open('test_api_result.txt', 'w') as f:
        f.write(data.decode('utf-8'))
except Exception as e:
    with open('test_api_result.txt', 'w') as f:
        f.write(str(e))
