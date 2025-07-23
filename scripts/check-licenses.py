#!/usr/bin/env python3
"""
Copyright 2025 MaaS Team

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
许可证合规检查脚本

此脚本用于检查项目依赖的许可证合规性，确保所有依赖都与 Apache 2.0 许可证兼容。
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set

# 与 Apache 2.0 兼容的许可证列表
COMPATIBLE_LICENSES = {
    "MIT",
    "MIT License",
    "BSD",
    "BSD License",
    "BSD-2-Clause",
    "BSD-3-Clause", 
    "Apache-2.0",
    "Apache License 2.0",
    "Apache Software License",
    "ISC",
    "ISC License",
    "Python Software Foundation License",
    "PSF",
    "Unlicense",
    "Public Domain",
    "CC0-1.0",
    "CC-BY-4.0",  # Creative Commons Attribution 4.0 用于数据
    "MPL-2.0",    # Mozilla Public License 2.0 - 与 Apache 2.0 兼容
    "BlueOak-1.0.0",  # Blue Oak Model License 1.0.0 - 宽松许可证
    "Python-2.0",     # Python 2.0 许可证 - 宽松许可证
}

# 不兼容的许可证列表
INCOMPATIBLE_LICENSES = {
    "GPL",
    "GPL-2.0",
    "GPL-3.0",
    "LGPL",
    "LGPL-2.1", 
    "LGPL-3.0",
    "AGPL",
    "AGPL-3.0",
    "Copyleft",
    "Commercial",
    "Proprietary",
}

# 需要特殊审查的许可证
REVIEW_REQUIRED = {
    "LGPL with exceptions",
    "Mozilla Public License",
    "MPL-2.0",
    "Eclipse Public License",
    "EPL-1.0",
    "EPL-2.0",
}


def check_python_licenses() -> Dict[str, List[str]]:
    """检查 Python 依赖的许可证"""
    print("🔍 检查 Python 依赖许可证...")
    
    try:
        # 使用 pip-licenses 检查许可证
        result = subprocess.run(
            ["pip-licenses", "--format=json", "--with-urls"],
            capture_output=True,
            text=True,
            cwd="maas-server"
        )
        
        if result.returncode != 0:
            print("⚠️  pip-licenses 未安装，尝试安装...")
            subprocess.run(["pip", "install", "pip-licenses"], check=True)
            result = subprocess.run(
                ["pip-licenses", "--format=json", "--with-urls"],
                capture_output=True,
                text=True,
                cwd="maas-server"
            )
        
        licenses_data = json.loads(result.stdout)
        
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        print("⚠️  无法自动检查 Python 许可证，请手动验证")
        return {"compatible": [], "incompatible": [], "review": []}
    
    compatible = []
    incompatible = []
    review = []
    
    for package in licenses_data:
        name = package.get("Name", "Unknown")
        license_name = package.get("License", "Unknown")
        
        if any(lic in license_name for lic in COMPATIBLE_LICENSES):
            compatible.append(f"{name}: {license_name}")
        elif any(lic in license_name for lic in INCOMPATIBLE_LICENSES):
            incompatible.append(f"{name}: {license_name}")
        else:
            review.append(f"{name}: {license_name}")
    
    return {
        "compatible": compatible,
        "incompatible": incompatible, 
        "review": review
    }


def check_npm_licenses() -> Dict[str, List[str]]:
    """检查 NPM 依赖的许可证"""
    print("🔍 检查 NPM 依赖许可证...")
    
    try:
        # 使用 license-checker 检查许可证
        result = subprocess.run(
            ["npx", "license-checker", "--json"],
            capture_output=True,
            text=True,
            cwd="maas-web"
        )
        
        if result.returncode != 0:
            print("⚠️  license-checker 未安装，尝试安装...")
            subprocess.run(["npm", "install", "-g", "license-checker"], check=True)
            result = subprocess.run(
                ["npx", "license-checker", "--json"],
                capture_output=True,
                text=True,
                cwd="maas-web"
            )
        
        licenses_data = json.loads(result.stdout)
        
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        print("⚠️  无法自动检查 NPM 许可证，请手动验证")
        return {"compatible": [], "incompatible": [], "review": []}
    
    compatible = []
    incompatible = []
    review = []
    
    for package_name, package_info in licenses_data.items():
        # 跳过本地项目包
        if package_name.startswith("maas-web@") or package_name.startswith("maas-server@"):
            continue
            
        license_name = package_info.get("licenses", "Unknown")
        
        if isinstance(license_name, list):
            license_name = ", ".join(license_name)
        
        if any(lic in str(license_name) for lic in COMPATIBLE_LICENSES):
            compatible.append(f"{package_name}: {license_name}")
        elif any(lic in str(license_name) for lic in INCOMPATIBLE_LICENSES):
            incompatible.append(f"{package_name}: {license_name}")
        else:
            review.append(f"{package_name}: {license_name}")
    
    return {
        "compatible": compatible,
        "incompatible": incompatible,
        "review": review
    }


def generate_report(python_result: Dict, npm_result: Dict) -> None:
    """生成许可证检查报告"""
    print("\n" + "="*60)
    print("📋 许可证合规检查报告")
    print("="*60)
    
    # Python 依赖报告
    print(f"\n🐍 Python 依赖 (maas-server):")
    print(f"   ✅ 兼容: {len(python_result['compatible'])} 个")
    print(f"   ❌ 不兼容: {len(python_result['incompatible'])} 个")
    print(f"   ⚠️  需审查: {len(python_result['review'])} 个")
    
    # NPM 依赖报告
    print(f"\n📦 NPM 依赖 (maas-web):")
    print(f"   ✅ 兼容: {len(npm_result['compatible'])} 个")
    print(f"   ❌ 不兼容: {len(npm_result['incompatible'])} 个")
    print(f"   ⚠️  需审查: {len(npm_result['review'])} 个")
    
    # 详细信息
    all_incompatible = python_result['incompatible'] + npm_result['incompatible']
    all_review = python_result['review'] + npm_result['review']
    
    if all_incompatible:
        print(f"\n❌ 不兼容的许可证:")
        for item in all_incompatible:
            print(f"   - {item}")
    
    if all_review:
        print(f"\n⚠️  需要审查的许可证:")
        for item in all_review:
            print(f"   - {item}")
    
    # 总结
    total_issues = len(all_incompatible) + len(all_review)
    if total_issues == 0:
        print(f"\n🎉 所有依赖许可证都与 Apache 2.0 兼容！")
        return True
    else:
        print(f"\n⚠️  发现 {total_issues} 个需要处理的许可证问题")
        return False


def check_license_files() -> bool:
    """检查许可证文件是否存在"""
    print("\n🔍 检查许可证文件...")
    
    required_files = [
        "LICENSE",
        "NOTICE", 
        "CONTRIBUTING.md",
        "AUTHORS",
        "maas-server/THIRD-PARTY-LICENSES.md",
        "maas-web/THIRD-PARTY-LICENSES.md",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少以下许可证文件:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ 所有许可证文件都存在")
        return True


def main():
    """主函数"""
    print("🚀 OpenMaaS 许可证合规检查")
    print("="*60)
    
    # 检查许可证文件
    files_ok = check_license_files()
    
    # 检查依赖许可证
    python_result = check_python_licenses()
    npm_result = check_npm_licenses()
    
    # 生成报告
    licenses_ok = generate_report(python_result, npm_result)
    
    # 总结
    print("\n" + "="*60)
    if files_ok and licenses_ok:
        print("🎉 许可证合规检查通过！")
        sys.exit(0)
    else:
        print("❌ 许可证合规检查失败，请处理上述问题")
        sys.exit(1)


if __name__ == "__main__":
    main()