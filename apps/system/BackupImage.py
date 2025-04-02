import shutil
import subprocess
import tarfile
import time

from ufile import filemanager
import os
from localDeploy.models import LocalOrder


class Ufile(object):
    def __init__(self, image_url, orderid):
        # 设置上传host后缀,外网可用后缀形如 .cn-bj.ufileos.com (.ufile.cn-north-02.ucloud.cn为内网后缀）
        # self.upload_suffix = '.cn-bj.ufileos.com'
        self.upload_suffix = '.ufile.cn-north-02.ucloud.cn'
        # 设置下载host后缀，普通下载后缀即上传后缀，CDN下载后缀为 .ufile.ucloud.com.cn
        # self.download_suffix = '.cn-bj.ufileos.com'
        self.download_suffix = '.ufile.cn-north-02.ucloud.cn'
        # 账户公钥
        self.public_key = 'TOKEN_50b41e38-64f3-4f8c-9ef3-3adbc3c88895'
        # 账户私钥
        self.private_key = 'ddfe10d8-ab02-4a3e-8a99-46e33903c9db'
        # 空间名称
        self.bucket = 'image-package'
        # 上传时为本地目录，下载时为保存在本地的目录
        self.local_file_dir = None
        # 文件在空间中的名称
        self.put_key = None
        # 镜像地址，列表
        self.image_url = image_url
        # 本地化工单id，用于创建镜像包存放地址目录名
        self.orderid = orderid
        # 本地文件文件base目录
        self.baseDir = "/data/backupImage"
        # self.baseDir = "G:\\data\\backupImage"
        self.initialization_data()

    def initialization_data(self):
        """
        创建
        :return:
        """
        new_dir_path = os.path.join(self.baseDir, f"{self.orderid}")
        if not os.path.exists(new_dir_path):
            os.makedirs(new_dir_path)
        self.local_file_dir = new_dir_path

    def uploadFile(self, fileName):
        """
        上传文件至ucloud
        :return:
        """
        self.put_key = f"{self.orderid}.tar"
        self.update_backup_mirror_url(self.put_key + "正在上传...")
        put_ufile_handler = filemanager.FileManager(self.public_key, self.private_key, self.upload_suffix,
                                                    self.download_suffix)
        # 普通上传文件至空间
        ret, resp = put_ufile_handler.putfile(self.bucket, self.put_key, os.path.join(self.baseDir, fileName),
                                              header=None)
        if resp.status_code == 200:
            self.update_backup_mirror_url(self.put_key + "上传成功！")
        else:
            self.update_backup_mirror_url(self.put_key + "上传失败！")

    def downloadFile(self, fileName):
        """
        下载ucloud的文件
        :return:
        """
        self.put_key = fileName
        self.update_backup_mirror_url(fileName+"正在下载...")
        download_ufile_handler = filemanager.FileManager(self.public_key, self.private_key, self.upload_suffix,
                                                         self.download_suffix)
        # 从公共空间下载文件

        ret, resp = download_ufile_handler.download_file(self.bucket, self.put_key,
                                                         os.path.join(self.local_file_dir, fileName), isprivate=False)
        if resp.status_code == 200:
            self.update_backup_mirror_url(fileName + "下载成功！")
        else:
            self.update_backup_mirror_url(fileName + "下载失败！")

    def backupImage(self):
        """
        根据地址到ucloud下载相应的tar包放到指定的目录下。然后把存放tar包的目录压缩再上传到ucloud
        :return:
        """
        if self.image_url:
            for imageItem in self.image_url:
                self.downloadFile(imageItem)
        self.make_tarfile()
        download_url = "https://image-package.cn-bj.ufileos.com/"+self.put_key
        self.update_backup_mirror_url("镜像包下载地址："+download_url)
        shutil.rmtree(self.local_file_dir)
        file_path = os.path.join(self.baseDir, f"{self.orderid}.tar")
        if os.path.exists(file_path):
            os.remove(file_path)

    def make_tarfile(self):
        """
        把/data/backupImage/image20下的文件压缩成tar存放在/data/backupImage/20.tar
        :return:
        """
        self.put_key = f"{self.orderid}.tar"
        # 使用tarfile压缩的tar包容易出现无法解压的问题
        # with tarfile.open(os.path.join(self.baseDir, self.put_key), "w:gz") as tar:
        #     tar.add(self.local_file_dir, arcname=os.path.basename(self.local_file_dir))
        # 使用subprocess执行系统中的文件压缩
        result = subprocess.run(['tar', '-cf', os.path.join(self.baseDir, self.put_key), '-C', self.baseDir, str(self.orderid)])
        # 检查压缩是否成功
        if result.returncode == 0:
            self.uploadFile(self.put_key)
        else:
            self.update_backup_mirror_url({result.returncode} + "压缩失败！")

    def update_backup_mirror_url(self, messages):
        """
        更新本地化工单表的backup_mirror_url
        :param messages:
        :return:
        """
        record = LocalOrder.objects.get(id=self.orderid)
        record.backup_mirror_url = messages
        record.save()
        time.sleep(0.1)


