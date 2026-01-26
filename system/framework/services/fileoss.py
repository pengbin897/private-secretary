import alibabacloud_oss_v2 as oss


class OssService:
    def __init__(self):
        self.OSS_ACCESS_KEY_ID = 'LTAI5tL9K3qUEughJZMJWhU9'
        self.OSS_ACCESS_KEY_SECRET = 'SFaCR3E58EUfkySxeoTy1c3LWQc8LL'
        credentials_provider = oss.credentials.StaticCredentialsProvider(self.OSS_ACCESS_KEY_ID, self.OSS_ACCESS_KEY_SECRET)

        # 加载SDK的默认配置，并设置凭证提供者
        cfg = oss.config.load_default()
        cfg.credentials_provider = credentials_provider
        cfg.region = 'cn-shenzhen' 

        self.client = oss.Client(cfg)

    def upload_file(self, file_path, file_name):
        # 定义要上传的字符串内容
        text_string = "Hello, OSS!"
        data = text_string.encode('utf-8')  # 将字符串编码为UTF-8字节串

        # 执行上传对象的请求，指定存储空间名称、对象名称和数据内容
        result = self.client.put_object(oss.PutObjectRequest(
            bucket="Your Bucket Name",
            key="Your Object Key",
            body=data,
        ))





