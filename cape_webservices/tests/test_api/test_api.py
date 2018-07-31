import requests

from cape_webservices.tests.tests_settings import URL

# pytest automatically imports cape_client and cape_client_answer fixtures in conftest.py

BASE_URL = URL + '/api/0.1'


def test_api(cape_client):
    token = cape_client.get_user_token()
    response = requests.get(BASE_URL + '/test?token=' + token)
    assert response.status_code == 200
    assert response.json()['success'] is True


def test_incomplete1(cape_client):
    token = cape_client.get_user_token()
    response = requests.get(BASE_URL + '/answer?token=' + token)
    assert response.status_code == 500
    assert response.json()['success'] is False
    assert 'question' in response.json()['result']['message']


def test_answer(cape_client):
    token = cape_client.get_user_token()
    response = requests.get(
        BASE_URL + f'/answer?token={token}&sourceType=document&question=How many potatoes do you have?')
    print(response.json())
    assert response.status_code == 200
    assert response.json()['success'] is True


def test_answer_inline(cape_client):
    token = cape_client.get_user_token()
    response = requests.get(
        BASE_URL + f'/answer?token={token}&sourceType=document&question=How many potatoes do you have?&text=I have 3 potatoes')
    print(response.json())
    assert response.status_code == 200
    assert response.json()['success'] is True


def test_exception_token_answer(cape_client):
    token = cape_client.get_user_token()
    params = {'token': token,
              'documentsOnly': 'true',
              'question': 'How many potatoes do you have?'}
    response = requests.post(BASE_URL + '/answer', params)

    print(response.json())
    assert response.status_code == 500
    assert response.json()['success'] is False


def test_json_list_in_json_request(cape_client):
    admintoken = cape_client.get_admin_token()
    response = requests.post(
        BASE_URL + '/saved-replies/get-saved-replies?adminToken=' + admintoken,
        "{\"savedReplyIds\":[\"fakeid\"]}")
    assert response.status_code == 200
    assert response.json()['success'] is True and len(response.json()['result']['items']) == 0


def test_plan_and_terms_agreed_and_onboarding(cape_client_answer):
    admintoken = cape_client_answer.get_admin_token()
    profile = cape_client_answer.get_profile()
    assert profile == {'username': 'testuser_answer', 'plan': 'free', 'termsAgreed': False, 'onboardingCompleted':False,'forwardEmail':None,'forwardEmailVerified':False}
    for plan in ['basic','free','pro']:
        response = requests.post(BASE_URL+'/user/set-plan?adminToken='+admintoken,{'plan':plan})
        assert response.status_code == 200
        assert response.json()['success'] is True
        assert response.json()['result']['plan'] == plan
    response = requests.post(BASE_URL + '/user/set-terms-agreed?adminToken=' + admintoken)
    assert response.status_code == 200
    assert response.json()['success'] is True
    assert response.json()['result']['termsAgreed'] is True
    response = requests.post(BASE_URL + '/user/set-onboarding-completed?adminToken=' + admintoken)
    assert response.status_code == 200
    assert response.json()['success'] is True
    assert response.json()['result']['onboardingCompleted'] is True
    response = requests.post(BASE_URL + '/user/get-profile?adminToken=' + admintoken)
    assert response.status_code == 200
    assert response.json()['success'] is True
    assert response.json()['result'] == {'username': 'testuser_answer', 'plan': 'pro', 'termsAgreed': True,'onboardingCompleted':True,'forwardEmail': None,'forwardEmailVerified':False}


def test_stats(cape_client):
    admin_token = cape_client.get_admin_token()
    response = requests.get(BASE_URL + f'/user/stats?adminToken=' + admin_token)
    assert response.status_code == 200
    assert response.json()['success'] is True
