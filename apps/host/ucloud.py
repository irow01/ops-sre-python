import json
import requests


class UCloudApi:

    def __init__(self, publicKey, signature, Region, ProjectId, action='DescribeUHostInstance'):
        self.ApiServer = 'http://api.ucloud.cn',
        self.PublicKey = publicKey,
        self.Signature = signature,
        self.Region = Region,
        self.Action = action,
        self.ProjectId = ProjectId,

    def get_host_info(self):
        params = {"PublicKey": self.PublicKey, "Limit": 300, "Signature": self.Signature,
                  "Region": self.Region, "ProjectId": self.ProjectId, "Action": self.Action}
        res = requests.get("http://api.ucloud.cn/", params=params)
        if res.status_code == 200:
            text = json.loads(res.text)
            return text
