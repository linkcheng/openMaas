#!/usr/bin/env python3
"""配置管理CLI工具"""

import os
import sys
import argparse
import asyncio
from pathlib import Path
from typing import Any, Dict, Optional

from config import get_settings, reload_settings
from config.config_utils import (
    ConfigSecurity, 
    ConfigValidator, 
    ConfigHealthChecker,
    get_config_summary,
    validate_config
)


class ConfigCLI:
    """配置管理CLI工具"""
    
    def __init__(self):
        self.security = ConfigSecurity()
        
    def show_config(self) -> None:
        """显示当前配置"""
        settings = get_settings()
        mask_secrets = bool(settings.environment=='production')
        summary = get_config_summary(settings, mask_secrets=mask_secrets)
        
        print("📋 当前配置信息:")
        print(f"  环境: {summary['environment']}")
        print(f"  调试模式: {summary['debug']}")
        print(f"  应用名称: {summary['app_name']}")
        print(f"  应用版本: {summary['app_version']}")
        print()
        
        print("🗄️  数据库配置:")
        print(f"  URL: {summary['database']['url']}")
        print()
        
        print("🔴 Redis配置:")
        print(f"  URL: {summary['redis']['url']}")
        print()
        
        print("🔒 安全配置:")
        print(f"  JWT密钥: {summary['security']['jwt_secret_key']}")
        print(f"  CORS源: {summary['security']['cors_origins']}")
        print()
    
    def validate_config(self) -> None:
        """验证配置"""
        print("🔍 验证配置...")
        
        result = validate_config()
        validation_results = result['validation_results']
        
        if not validation_results:
            print("✅ 配置验证通过！")
            return
        
        print("❌ 配置验证失败:")
        for category, errors in validation_results.items():
            print(f"\n📂 {category}:")
            for error in errors:
                print(f"  ❌ {error}")
    
    async def health_check(self) -> None:
        """健康检查"""
        print("🏥 执行健康检查...")
        
        settings = get_settings()
        checker = ConfigHealthChecker(settings)
        
        try:
            results = await checker.check_all_connections()
            
            print("\n📊 健康检查结果:")
            for service, status in results.items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {service}: {'健康' if status else '异常'}")
            
            failed_services = [s for s, status in results.items() if not status]
            if failed_services:
                print(f"\n⚠️  失败的服务: {', '.join(failed_services)}")
            else:
                print("\n🎉 所有服务都正常运行！")
                
        except Exception as e:
            print(f"❌ 健康检查失败: {e}")
    
    def encrypt_value(self, value: str) -> None:
        """加密配置值"""
        encrypted = self.security.encrypt_value(value)
        print(f"🔒 加密后的值: {encrypted}")
    
    def decrypt_value(self, encrypted_value: str) -> None:
        """解密配置值"""
        decrypted = self.security.decrypt_value(encrypted_value)
        print(f"🔓 解密后的值: {decrypted}")
    
    def show_env_info(self) -> None:
        """显示环境信息"""
        current_env = os.getenv("MAAS_ENVIRONMENT", "development")
        print(f"🌍 当前环境: {current_env}")
        
        config_dir = Path(__file__).parent / "config" / "environments"
        env_files = list(config_dir.glob("*.env"))
        
        if env_files:
            print(f"📁 可用的配置文件:")
            for file in env_files:
                print(f"  ✅ {file.name}")
        else:
            print("❌ 未找到配置文件")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="MaaS Platform 配置管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python manage_config.py show                    # 显示当前配置
  python manage_config.py validate               # 验证配置
  python manage_config.py health                 # 健康检查
  python manage_config.py encrypt "secret"       # 加密配置值
  python manage_config.py decrypt "encrypted"    # 解密配置值
  python manage_config.py env                    # 显示环境信息
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # show 命令
    show_parser = subparsers.add_parser("show", help="显示当前配置")
    
    # validate 命令
    subparsers.add_parser("validate", help="验证配置")
    
    # health 命令
    subparsers.add_parser("health", help="健康检查")
    
    # encrypt 命令
    encrypt_parser = subparsers.add_parser("encrypt", help="加密配置值")
    encrypt_parser.add_argument("value", help="要加密的值")
    
    # decrypt 命令
    decrypt_parser = subparsers.add_parser("decrypt", help="解密配置值")
    decrypt_parser.add_argument("value", help="要解密的值")
    
    # env 命令
    subparsers.add_parser("env", help="显示环境信息")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = ConfigCLI()
    
    try:
        if args.command == "show":
            cli.show_config()
        elif args.command == "validate":
            cli.validate_config()
        elif args.command == "health":
            await cli.health_check()
        elif args.command == "encrypt":
            cli.encrypt_value(args.value)
        elif args.command == "decrypt":
            cli.decrypt_value(args.value)
        elif args.command == "env":
            cli.show_env_info()
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())