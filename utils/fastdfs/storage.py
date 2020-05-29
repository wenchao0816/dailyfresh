# coding=utf-8
from fdfs_client.client import Fdfs_client

from django.core.files.storage import Storage
from django.conf import settings

class FDFSStorage(Storage):

    def __init__(self, client_conf_path=None, url_ip=None):
        if client_conf_path is None:
            client_conf_path = settings.CLIENT_CONF_PATH
        self.client_conf_path = client_conf_path
        if url_ip is None:
            url_ip = settings.URL_IP
        self.url_ip = url_ip

    def open(self, name, mode='rb'):
        pass

    def save(self, name, content, max_length=None):
        fdfs = Fdfs_client(self.client_conf_path)
        rest = fdfs.upload_appender_by_buffer(content.read())
        if rest.get('Status') != 'Upload successed.':
            raise Exception('上传文件失败！')
        return rest.get('Remote file_id')

    def exists(self, name):
        return False

    def url(self, name):
        return self.url_ip+'/'+name
