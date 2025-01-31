import requests
import os
from dotenv import load_dotenv

load_dotenv()

def ping():
    headers = {
        'x-api-key': os.getenv('ETSY_API_KEY')
    }
    try:
        response = requests.get('https://api.etsy.com/v3/application/openapi-ping', headers=headers)
        if response.ok:
            return {"status": "success", "response": response.json()}
        return {"status": "error", "message": f"Error: {response.status_code}", "details": response.text}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    print(ping())