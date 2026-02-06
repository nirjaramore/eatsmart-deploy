from fastapi.testclient import TestClient
import os
os.chdir(r'C:\Users\anany\projects\eatsmart\eatsmartly-backend')
from main import app

client = TestClient(app)
resp = client.options('/extract-text', headers={'Origin':'http://localhost:3001', 'Access-Control-Request-Method':'POST'})
print('status', resp.status_code)
print('cors headers:')
for k, v in resp.headers.items():
    if 'access-control' in k.lower():
        print(f'{k}: {v}')
print('\nbody (first 200 chars):')
print(resp.text[:200])
