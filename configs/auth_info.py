import os

authInfo = {
    'client_id': os.environ.get('CLIENT_ID', 'blazebank'),
    'client_secret': os.environ.get('CLIENT_SECRET', 'ez6yvtKKyzyUP265ZW7f5SPb6a30NA5W'),
    'realm': os.environ.get('REALM_NAME', 'blazebank')
}