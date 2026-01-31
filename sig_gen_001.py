#Working 
from Crypto.PublicKey import RSA
import os
os.system('openssl genrsa -out private_key.pem 1024')
k = RSA.importKey(open('private_key.pem').read())
with open('public_key.pem','w') as f: 
    f.write(k.publickey().exportKey().decode('utf-8'))
print('BOTH keys ready!')