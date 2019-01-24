from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.utils.deconstruct import deconstructible
from mall import settings

# 1 您的自定义存储系统必须是以下子类 django.core.files.storage.Storage：
# 4 您的存储类必须是可解构的， 以便在迁移中的字段上使用它时可以对其进行序列化。
# 只要您的字段具有可自行序列化的参数，
# 就 可以使用 django.utils.deconstruct.deconstructible类装饰器（这就是Django在FileSystemStorage上使用的）。
@deconstructible
class MyStorage(Storage):

    # 2 Django必须能够在没有任何参数的情况下实例化您的存储系统。这意味着任何设置都应该来自django.conf.settings
    def __init__(self, config_path=None, config_url=None):
        if not config_path:
            fdfs_config = settings.FDFS_CLIENT_CONF
            self.fdfs_config = fdfs_config
        if not config_url:
            fdfs_url = settings.FDFS_URL
            self.fdfs_url = fdfs_url
    # 3 您的存储类必须实现_open()和_save() 方法
    # 以及适用于您的存储类的任何其他方法。

    # 因为我们的Fdfs是通过http来获取图片的，所以不需要打开方法
    def _open(self,name,mode='rb'):
        pass


    def _save(self, name, content, max_length=None):
        # name,   文件的名字　　不能通过名字获取完整路径
        # content,  　内容　就是上传的内容　　二进制
        # max_length=None
        #1 创建Fdfs的客户端，让客户端加载配置文件
        # client = Fdfs_client(settings.FDFS_CLIENT_CONF)
        client = Fdfs_client(self.fdfs_config)

        #2 获取上传的文件

        # content.read()  就是读取content的内容
        # 读取的是二进制
        file_data = content.read()
        #3 上传图片　获取返回内容
        result = client.upload_by_buffer(file_data)
        #4 根据返回内容　获取
        """
        {'Remote file_id': 'group1/M00/00/00/wKi9nFw-ryGAbRnmAAj_Z8-Ye88346.jpg',
        'Uploaded size': '575.00KB',
        'Local file name': '/home/python/Desktop/A180900946/1.jpg',
        'Storage IP': '192.168.189.156',
        'Status': 'Upload successed.',
         'Group name': 'group1'}

        """
        if result.get('Status') == 'Upload successed.':
            # 说明上传成功
            file_id = result.get('Remote file_id')
        else:
            raise Exception('上传失败')

        # 把file_id返回回去
        return file_id


    # exists存在
    # Fdfs做了重名的处理　我们只需要上传就可以
    def exists(self, name):
        return False

    def url(self,name):
        # 默认调用　storage的url方法　会返回name(file_id)
        # 实际我们访问图片的时候　是通过http://id:端口号
        return self.fdfs_url + name
# docker run -dti --network=host --name storage -e TRACKER_SERVER=192.168.189.156:22122 -v /var/fdfs/storage:/var/fdfs delron/fastdfs storage

