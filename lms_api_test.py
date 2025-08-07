import requests

BASE_URL = "http://127.0.0.1:8000"

USERNAME = "PAPA"  # Remplace par ton login
PASSWORD = "1234512345"  # Remplace par ton mot de passe (Removed leading space)


def get_tokens(username, password):
    url = f"{BASE_URL}/api/token/"
    # CORRECTED: Use the 'username' and 'password' variables passed to the function
    data = {"username": username, "password": password}
    resp = requests.post(url, json=data)
    resp.raise_for_status()  # This will raise an HTTPError for bad responses (4xx or 5xx)
    return resp.json()  # Contains access and refresh tokens


def refresh_access_token(refresh_token):
    url = f"{BASE_URL}/api/token/refresh/"
    data = {"refresh": refresh_token}
    resp = requests.post(url, json=data)
    resp.raise_for_status()
    return resp.json()["access"]


def get_courses(access_token):
    url = f"{BASE_URL}/api/courses/"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers)
    # The 'if resp.status_code == 401:' block is redundant if resp.raise_for_status() is used,
    # as raise_for_status() will turn a 401 into an exception caught by the main try/except.
    # If you want specific 401 handling, you'd typically remove raise_for_status() and
    # handle different status codes explicitly, or catch the HTTPError and check its status_code.
    resp.raise_for_status()
    return resp.json()


def main():
    try:
        # 1. Login and get tokens
        tokens = get_tokens(USERNAME, PASSWORD)
        access_token = tokens["access"]
        refresh_token = tokens["refresh"]
        print("Tokens obtenus !")
        print(
            f"Access Token (truncated): {access_token[:20]}..."
        )  # Added truncation for security
        print(
            f"Refresh Token (truncated): {refresh_token[:20]}..."
        )  # Added truncation for security

        # 2. Call API courses with access token
        courses = get_courses(access_token)
        print("Courses:", courses)

        # 3. Refresh token if needed (example)
        # In a real application, you'd typically refresh the token only when
        # an API call fails with a 401 (Unauthorized) due to an expired access token.
        new_access_token = refresh_access_token(refresh_token)
        print("Nouveau token access obtenu !")
        print(
            f"Nouveau Access Token (truncated): {new_access_token[:20]}..."
        )  # Added truncation

    except requests.HTTPError as e:
        # Improved error message to include status code and response body
        print(f"Erreur HTTP: {e.response.status_code} - {e.response.text}")
    except KeyError as e:
        # Added specific handling for missing keys in JSON response
        print(
            f"Erreur: Clé manquante dans la réponse du serveur: {e}. Vérifiez la structure JSON des tokens."
        )
    except Exception as e:
        print("Une erreur inattendue est survenue:", str(e))


if __name__ == "__main__":
    main()
