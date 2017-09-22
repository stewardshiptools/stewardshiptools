import time
from django.contrib.auth.models import User


def create_test_user_and_log_in(test_client):
    # print ("Creating test user.")
    u = 'test_user'
    p = '123454243'
    user = User.objects.create(username=u)
    user.set_password(p)
    user.save()
    logged_in = test_client.login(username=u, password=p)
    # print("Test user logged in:", logged_in)
    return test_client


def function_timer(func_to_call, *func_args):
    start = time.clock()
    result = func_to_call(*func_args)
    elapsed = time.clock() - start
    return elapsed, result
