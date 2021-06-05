import requests

files = {'wav': ('audio1.wav', open('/Users/markbaushenko/Desktop/test_true_wav/english_8khz16bitmono.wav', 'rb'), 'audio/wave')}

response = requests.post('http://127.0.0.1:5001/recognize', files=files)
print(response.text)
