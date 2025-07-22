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
许可证头部添加脚本

此脚本用于为项目中的源代码文件添加 Apache 2.0 许可证头部。
"""

import os
import re
from pathlib import Path
from typing import Dict, List

# 许可证头部模板
LICENSE_HEADERS = {
    "python": '''"""
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
"""''',
    
    "typescript": '''/*
 * Copyright 2025 MaaS Team
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */''',
    
    "vue": '''<!--
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
-->''',
    
    "shell": '''#!/bin/bash
#
# Copyright 2025 MaaS Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#''',
}

# 文件类型映射
FILE_TYPE_MAPPING = {
    ".py": "python",
    ".ts": "typescript", 
    ".js": "typescript",
    ".vue": "vue",
    ".sh": "shell",
    ".bash": "shell",
}

# 需要跳过的文件和目录
SKIP_PATTERNS = {
    # 目录
    "node_modules",
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "dist",
    "build",
    ".nuxt",
    ".output",
    "coverage",
    
    # 文件
    "package-lock.json",
    "yarn.lock",
    "uv.lock",
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    "LICENSE",
    "NOTICE",
    "README.md",
    "CONTRIBUTING.md",
    "AUTHORS",
}

# 已有许可证头部的检测模式
LICENSE_PATTERNS = [
    r"Copyright.*\d{4}",
    r"Licensed under the Apache License",
    r"SPDX-License-Identifier",
    r"@license",
]


def has_license_header(content: str) -> bool:
    """检查文件是否已有许可证头部"""
    # 只检查文件前1000个字符
    header_content = content[:1000]
    
    for pattern in LICENSE_PATTERNS:
        if re.search(pattern, header_content, re.IGNORECASE):
            return True
    
    return False


def get_file_type(file_path: Path) -> str:
    """根据文件扩展名确定文件类型"""
    suffix = file_path.suffix.lower()
    return FILE_TYPE_MAPPING.get(suffix, "")


def should_skip_file(file_path: Path) -> bool:
    """判断是否应该跳过文件"""
    # 检查文件名
    if file_path.name in SKIP_PATTERNS:
        return True
    
    # 检查路径中的目录
    for part in file_path.parts:
        if part in SKIP_PATTERNS:
            return True
    
    # 检查文件扩展名
    if file_path.suffix in [".json", ".md", ".txt", ".yml", ".yaml", ".toml", ".ini"]:
        return True
    
    return False


def add_license_header(file_path: Path, dry_run: bool = False) -> bool:
    """为文件添加许可证头部"""
    if should_skip_file(file_path):
        return False
    
    file_type = get_file_type(file_path)
    if not file_type:
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        print(f"⚠️  无法读取文件: {file_path}")
        return False
    
    # 检查是否已有许可证头部
    if has_license_header(content):
        return False
    
    # 获取许可证头部
    license_header = LICENSE_HEADERS.get(file_type, "")
    if not license_header:
        return False
    
    # 处理 shebang 行
    new_content = content
    if file_type == "python" and content.startswith("#!"):
        lines = content.split('\n', 1)
        shebang = lines[0]
        rest_content = lines[1] if len(lines) > 1 else ""
        new_content = f"{shebang}\n{license_header}\n\n{rest_content}"
    elif file_type == "shell":
        # shell 脚本的许可证头部已包含 shebang
        if content.startswith("#!"):
            lines = content.split('\n', 1)
            rest_content = lines[1] if len(lines) > 1 else ""
            new_content = f"{license_header}\n\n{rest_content}"
        else:
            new_content = f"{license_header}\n\n{content}"
    else:
        new_content = f"{license_header}\n\n{content}"
    
    if dry_run:
        print(f"📝 将添加许可证头部: {file_path}")
        return True
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ 已添加许可证头部: {file_path}")
        return True
    except PermissionError:
        print(f"❌ 无权限写入文件: {file_path}")
        return False


def scan_directory(directory: Path, dry_run: bool = False) -> Dict[str, int]:
    """扫描目录并添加许可证头部"""
    stats = {
        "processed": 0,
        "skipped": 0,
        "added": 0,
        "errors": 0,
    }
    
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            stats["processed"] += 1
            
            if should_skip_file(file_path):
                stats["skipped"] += 1
                continue
            
            try:
                if add_license_header(file_path, dry_run):
                    stats["added"] += 1
                else:
                    stats["skipped"] += 1
            except Exception as e:
                print(f"❌ 处理文件时出错 {file_path}: {e}")
                stats["errors"] += 1
    
    return stats


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="为源代码文件添加 Apache 2.0 许可证头部")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际修改文件")
    parser.add_argument("--directory", default=".", help="要处理的目录路径")
    
    args = parser.parse_args()
    
    directory = Path(args.directory)
    if not directory.exists():
        print(f"❌ 目录不存在: {directory}")
        return
    
    print("🚀 OpenMaaS 许可证头部添加工具")
    print("="*60)
    
    if args.dry_run:
        print("🔍 预览模式 - 不会实际修改文件")
    
    print(f"📁 扫描目录: {directory.absolute()}")
    
    # 扫描并处理文件
    stats = scan_directory(directory, args.dry_run)
    
    # 输出统计信息
    print("\n" + "="*60)
    print("📊 处理统计:")
    print(f"   📄 总文件数: {stats['processed']}")
    print(f"   ✅ 添加头部: {stats['added']}")
    print(f"   ⏭️  跳过文件: {stats['skipped']}")
    print(f"   ❌ 错误文件: {stats['errors']}")
    
    if args.dry_run and stats['added'] > 0:
        print(f"\n💡 运行 'python {__file__} --directory {directory}' 来实际添加许可证头部")
    elif stats['added'] > 0:
        print(f"\n🎉 成功为 {stats['added']} 个文件添加了许可证头部！")
    else:
        print(f"\n✨ 所有文件都已有许可证头部或被跳过")


if __name__ == "__main__":
    main()