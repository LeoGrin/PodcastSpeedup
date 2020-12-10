import urllib.request
from urllib.error import HTTPError
import re

#
# Takes a url and a directory for saving the file. Directory must exist.
#
def download(url, dir_name, file_name, preserve_extension):
    file_name = re.findall(r"^.*\.(?:mp3|wav)", url.split('/')[-1])[0]  # exctract the file name
    file_extension = file_name.split(".")[-1]
    #if is_audio_link:
    #    file_name = re.findall(r"^.*\.(?:mp3|wav)", url.split('/')[-1])[0] #exctract the file name
    #else:
    #change user-agent to bypass error 403 on some feeds
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    u = urllib.request.urlopen(req)

    if preserve_extension:
        f = open(dir_name + '/' + file_name + "." + file_extension, 'wb')
    else:
        f = open(dir_name + '/' + file_name, 'wb')
    file_size = int(int(u.info()["Content-Length"]) / 1e3)
    print("Downloading File: %s (Size: %s Kb)" % (file_name, file_size))
    print_every = 100
    iter = 0
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        file_size_dl_mb = file_size_dl / 1e3
        f.write(buffer)
        if iter % print_every == 0:
            status = "{} Kb  [{}%]".format(int(file_size_dl_mb), int(file_size_dl_mb * 100. / file_size))
            status = status + "\n"
            print(status)
        iter += 1

    f.close()

    return file_name, file_extension

    #if is_audio_link:
    #    file_name = re.findall(r"^.*\.(?:mp3|wav)", url.split('/')[-1])[0] #exctract the file name
    #else:
    #change user-agent to bypass error 403 on some feeds
