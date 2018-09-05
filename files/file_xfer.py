def _upload(host, creds, fp):
 
    chunk_size = 512 * 1024
    headers = {
        'Content-Type': 'application/octet-stream'
    }
    fileobj = open(fp, 'rb')
    filename = os.path.basename(fp)
    if os.path.splitext(filename)[-1] == '.iso':
        uri = 'https://%s/mgmt/cm/autodeploy/software-image-uploads/%s' % (host, filename)
    else:
        uri = 'https://%s/mgmt/shared/file-transfer/uploads/%s' % (host, filename)
 
    #requests.packages.urllib3.disable_warnings()
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    size = os.path.getsize(fp)
 
    start = 0
 
    while True:
        file_slice = fileobj.read(chunk_size)
        if not file_slice:
            break
 
        current_bytes = len(file_slice)
        if current_bytes < chunk_size:
            end = size
        else:
            end = start + current_bytes
 
        content_range = "%s-%s/%s" % (start, end - 1, size)
        headers['Content-Range'] = content_range
        requests.post(uri,
                      auth=creds,
                      data=file_slice,
                      headers=headers,
                      verify=False)
 
        start += current_bytes
 
if __name__ == "__main__":
    import os, requests, argparse, urllib3, getpass
 
    parser = argparse.ArgumentParser(description='Upload File to BIG-IP')
 
    parser.add_argument("host", help='BIG-IP IP or Hostname', )
    parser.add_argument("username", help='BIG-IP Username', )
    parser.add_argument("password", help='BIG-IP Password')
    parser.add_argument("filepath", help='Source Filename with Absolute Path')
    args = vars(parser.parse_args())
 
    hostname = args['host']
    username = args['username']
    password = args['password']
    filepath = args['filepath']
 
    #print "%s, enter your password: " % args['username'],
    #password = getpass.getpass()
 
    _upload(hostname, (username, password), filepath)
