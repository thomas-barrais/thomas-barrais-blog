import requests
import json
import time

CLIENT_ID = '171267'
CLIENT_SECRET = '3f7eae767fcd9eb3e9d8a9c332d42dbd82e19d26'

# 1. COLLE TON CODE ICI POUR LE PREMIER LANCEMENT
AUTH_CODE = 'COLLE_TON_CODE_ICI'

TOKEN_FILE = 'strava_tokens.json'
ACTIVITIES_FILE = 'activites_strava.json'

def get_tokens():
    """Gère l'authentification et le rafraîchissement des jetons"""
    try:
        with open(TOKEN_FILE, 'r') as f:
            tokens = json.load(f)
    except FileNotFoundError:
        # Premier lancement : on échange le code contre les jetons
        print("Obtention des premiers jetons...")
        res = requests.post(
            'https://www.strava.com/oauth/token',
            data={
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'code': AUTH_CODE,
                'grant_type': 'authorization_code'
            }
        )
        tokens = res.json()
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f)

    # Si le jeton est expiré, on le rafraîchit (Strava les expire toutes les 6h)
    if tokens.get('expires_at', 0) < time.time():
        print("Jeton expiré, rafraîchissement en cours...")
        res = requests.post(
            'https://www.strava.com/oauth/token',
            data={
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'refresh_token': tokens['refresh_token'],
                'grant_type': 'refresh_token'
            }
        )
        new_tokens = res.json()
        tokens.update(new_tokens)
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f)
            
    return tokens['access_token']

def fetch_activities():
    """Télécharge toutes les activités"""
    access_token = get_tokens()
    url = "https://www.strava.com/api/v3/athlete/activities"
    header = {'Authorization': f'Bearer {access_token}'}
    
    all_activities = []
    page = 1
    
    print("Aspiration de la souffrance en cours...")
    while True:
        param = {'per_page': 200, 'page': page}
        dataset = requests.get(url, headers=header, params=param).json()
        
        if len(dataset) == 0:
            break
            
        all_activities.extend(dataset)
        print(f"Page {page} aspirée ({len(dataset)} courses).")
        page += 1

    # On sauvegarde tout ça dans un beau fichier JSON
    with open(ACTIVITIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_activities, f, ensure_ascii=False, indent=4)
        
    print(f"\nTerminé ! {len(all_activities)} activités sauvegardées dans {ACTIVITIES_FILE}.")

if __name__ == '__main__':
    fetch_activities()