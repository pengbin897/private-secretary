from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction

from system.models import UserManageAccount
from system.common.constant import UserChannel


class Command(BaseCommand):
    help = '创建一个普通用户，同时创建关联的 UserManageAccount 记录'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='用户名（必填）')
        parser.add_argument('--password', type=str, default='123456', help='密码（默认: 123456）')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = f"{username}@linkgeeks.com.cn"

        if User.objects.filter(username=username).exists():
            raise CommandError(f'用户 "{username}" 已存在')

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                )
                UserManageAccount.objects.create(
                    user=user,
                    channel=UserChannel.TRANDITIONAL,
                    balance=0,
                )
        except Exception as e:
            raise CommandError(f'创建用户失败: {e}')

        self.stdout.write(self.style.SUCCESS(
            f'用户 "{username}" 创建成功 (email: {email}, channel: TRANDITIONAL, balance: 0)'
        ))
