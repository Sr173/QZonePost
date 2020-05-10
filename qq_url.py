import trip

url = 'http://url.cn/5hj9gyQ'
s = trip.Session()

@trip.coroutine
def fetch(times=10000):
    yield [s.get(url, timeout=20, allow_redirects=False) for i in range(times)]

str_data = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"


trip.run(fetch)