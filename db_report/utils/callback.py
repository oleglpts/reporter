import json
import pycurl
from io import BytesIO
import multiprocessing
from urllib.parse import urlencode, unquote
from db_report.config import cmd_args, logger, translate as _
from bottle import route, run, request


@route('/', method='POST')
def bottle_callback():
    """

    Callback handler

    :return: response
    :rtype: str

    """
    logger.debug('%s: \'%s\'' % (_('callback received data'), unquote(request.body.read().decode())))
    return '{"result": "Ok"}'


server = multiprocessing.Process(target=lambda: run(host='localhost', port=8080, quiet=True))


def curl_request(url, raw=False, head=None, post_data=None, post_file=None, post_upload=None, credentials=None,
                 raw_data=False, patch=False):
    """

    Curl request

    :param url: request url
    :type url: str
    :param raw: return raw result
    :type raw: bool
    :param head: request http headers
    :type head: list
    :param post_data: post parameters
    :type post_data: dict
    :param post_file: name of file with post data in format p0=v0&p1=v1&...
    :type post_file: str
    :param post_upload: files for upload
    :type post_upload: list
    :param credentials: HTTP basic authentication credentials
    :type credentials: str
    :param raw_data: send raw (not urlencoded) data
    :type raw_data: bool
    :param patch: method PATCH
    :type patch: bool
    :return: response
    :rtype: dict

    """
    post_fields = None
    if post_file is not None:
        try:
            post_data = {parm.split('=')[0]: urlencode(parm.split('=')[1]) for parm in
                         open(post_file, 'r').read().split('&')}
        except FileNotFoundError:
            print('File %s not found' % post_file)
            return None
    c = pycurl.Curl()
    buf = BytesIO()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.WRITEFUNCTION, buf.write)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    if head is not None:
        c.setopt(pycurl.HTTPHEADER, head)
    if post_data is not None:
        if not raw_data:
            post_fields = urlencode(post_data)
        else:
            post_fields = post_data
        if not patch:
            c.setopt(c.POSTFIELDS, post_fields.encode())
    if post_upload is not None:
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.HTTPPOST, post_upload)
    if credentials is not None:
        c.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
        c.setopt(pycurl.USERPWD, credentials)
    if patch:
        c.setopt(pycurl.UPLOAD, 1)
        c.setopt(pycurl.CUSTOMREQUEST, 'PATCH')
        c.setopt(pycurl.READFUNCTION, BytesIO(post_fields.encode()).read)
        c.setopt(pycurl.INFILESIZE, len(post_fields.encode()))
    c.perform()
    c.close()
    try:
        response = json.loads(buf.getvalue().decode('UTF-8')) if not raw else buf.getvalue()
    except json.JSONDecodeError:
        response = {'result': buf.getvalue().decode('UTF-8')}
    return response


def callback(parameters):
    """

    Post callback

    :param parameters: post parameters for callback
    :type parameters: dict
    :return response
    :rtype: dict

    """
    try:
        if cmd_args.token:
            parameters['token'] = cmd_args.token
            response = curl_request(cmd_args.callback_url, post_data=parameters) if cmd_args.token is not None else None
        else:
            response = None
    except Exception as exc:
        response = {'result': str(exc)}
    return response


def callback_terminate(code, parameters):
    """

    Terminate program

    :param code: exit code
    :type code: int
    :param parameters: post parameters for callback
    :type parameters: dict

    """
    parameters['status'] = code
    if cmd_args.token:
        response = callback(parameters)
        logger.debug('%s: %s' % (_('callback response'), response.get('result', 'None')))
    if server.is_alive():
        server.terminate()
        server.join()
    logger.debug('%s: %s' % (_('reporter result'), json.dumps(parameters)))
    logger.info(_('reporter ended'))
    exit(code)
