#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 内置浏览器切换工具 (改进版)
===================================

一键启用/禁用 OpenClaw 内置浏览器

改进：
- 配置验证
- 热重载支持
- 增强的 Chrome 路径检测
- 配置预设支持

用法：
    python browser_toggle_improved.py --enable    # 启用内置浏览器
    python browser_toggle_improved.py --disable   # 禁用（恢复默认）
    python browser_toggle_improved.py --status    # 查看状态
    python browser_toggle_improved.py --headless  # 切换到无头模式
    python browser_toggle_improved.py --validate  # 验证配置
    python browser_toggle_improved.py --preset dev     # 开发模式
    python browser_toggle_improved.py --preset privacy # 隐私模式

作者：AI Assistant (改进版)
日期：2026-02-28
"""

import json
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BrowserToggle:
    """浏览器配置切换器（改进版）"""
    
    def __init__(self):
        # 配置文件路径
        self.config_file = Path.home() / ".openclaw" / "openclaw.json"
        self.backup_dir = Path.home() / ".openclaw" / "workspace" / "backups"
        
        # 确保备份目录存在
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 内置浏览器配置
        self.browser_config = {
            "browser": {
                "enabled": True,
                "defaultProfile": "openclaw",
                "headless": False,
                "noSandbox": False,
                "attachOnly": False,
                "executablePath": self._get_chrome_path()
            }
        }
    
    def _get_chrome_path(self) -> str:
        """获取 Chrome 安装路径（增强版）"""
        import platform
        system = platform.system()
        
        # 尝试动态检测
        chrome_paths = self._detect_chrome_paths()
        if chrome_paths:
            logger.info(f"检测到 Chrome 路径：{chrome_paths[0]}")
            return chrome_paths[0]
        
        # 回退到硬编码路径
        if system == "Windows":
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]
        elif system == "Darwin":  # macOS
            paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium"
            ]
        else:  # Linux
            paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
                "/snap/bin/chromium",
                "/usr/local/bin/chrome"
            ]
        
        # 返回第一个存在的路径
        for path in paths:
            if Path(path).exists():
                return path
        
        # 都不存在时返回默认
        return paths[0]
    
    def _detect_chrome_paths(self) -> List[str]:
        """动态检测 Chrome 路径"""
        import shutil
        paths = []
        
        # 尝试 which/where 命令
        chrome_commands = ["google-chrome", "chromium", "chromium-browser", "chrome"]
        for cmd in chrome_commands:
            result = shutil.which(cmd)
            if result:
                paths.append(result)
        
        return paths
    
    def load_config(self) -> Optional[Dict]:
        """加载配置文件"""
        if not self.config_file.exists():
            logger.error(f"配置文件不存在：{self.config_file}")
            return None
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            logger.error(f"加载配置失败：{e}")
            return None
    
    def save_config(self, config: Dict) -> bool:
        """保存配置文件"""
        try:
            # 先备份
            backup_file = self._backup_config()
            
            # 写入配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置已保存：{self.config_file}")
            logger.info(f"备份位置：{backup_file}")
            return True
        except Exception as e:
            logger.error(f"保存配置失败：{e}")
            return False
    
    def _backup_config(self) -> Optional[str]:
        """备份配置文件"""
        if not self.config_file.exists():
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_file = self.backup_dir / f"openclaw-{timestamp}-before-browser-toggle.json"
            shutil.copy2(self.config_file, backup_file)
            logger.info(f"配置已备份：{backup_file}")
            return str(backup_file)
        except Exception as e:
            logger.warning(f"备份失败：{e}")
            return None
    
    def restore_from_backup(self, backup_file: str) -> bool:
        """从备份恢复"""
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                logger.error(f"备份文件不存在：{backup_file}")
                return False
            
            shutil.copy2(backup_path, self.config_file)
            logger.info(f"配置已恢复：{backup_file}")
            return True
        except Exception as e:
            logger.error(f"恢复失败：{e}")
            return False
    
    def get_status(self) -> Dict:
        """获取当前状态"""
        config = self.load_config()
        if not config:
            return {"error": "无法加载配置"}
        
        browser_config = config.get("browser", {})
        is_enabled = browser_config.get("enabled", False)
        profile = browser_config.get("defaultProfile", "chrome")
        headless = browser_config.get("headless", True)
        exec_path = browser_config.get("executablePath", "auto")
        
        return {
            "enabled": is_enabled,
            "profile": profile,
            "headless": headless,
            "executable_path": exec_path,
            "mode": "内置浏览器" if is_enabled and profile == "openclaw" else "Chrome 扩展"
        }
    
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        logger.info("验证配置...")
        
        config = self.load_config()
        if not config:
            logger.error("❌ 无法加载配置")
            return False
        
        browser_config = config.get("browser", {})
        
        # 检查必需字段
        required_fields = ["enabled", "defaultProfile"]
        for field in required_fields:
            if field not in browser_config:
                logger.error(f"❌ 缺少必需字段：{field}")
                return False
        
        # 验证 Chrome 路径
        exec_path = browser_config.get("executablePath")
        if exec_path and not Path(exec_path).exists():
            logger.warning(f"⚠️ Chrome 路径不存在：{exec_path}")
            logger.info("提示：使用 --auto-detect 自动检测 Chrome 路径")
            return False
        
        # 验证 profile
        profile = browser_config.get("defaultProfile")
        # 支持自定义 profile（检查是否在 profiles 中定义）
        profiles = config.get("browser", {}).get("profiles", {})
        if profile not in ["openclaw", "chrome"] and profile not in profiles:
            logger.error(f"❌ 无效的 profile: {profile}")
            logger.info(f"可用 profile: openclaw, chrome, {', '.join(profiles.keys())}")
            return False
        
        logger.info("✅ 配置验证通过")
        return True
    
    def reload_gateway(self) -> bool:
        """热重载 Gateway"""
        logger.info("尝试热重载 OpenClaw Gateway...")
        
        try:
            # 尝试使用 openclaw 命令
            result = subprocess.run(
                ["openclaw", "gateway", "reload"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("✅ Gateway 已重载")
                return True
            else:
                logger.warning(f"⚠️ Gateway 重载失败：{result.stderr}")
                logger.info("请手动重启：openclaw gateway restart")
                return False
        except FileNotFoundError:
            logger.warning("⚠️ 未找到 openclaw 命令")
            logger.info("请手动重启：openclaw gateway restart")
            return False
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ Gateway 重载超时")
            logger.info("请手动重启：openclaw gateway restart")
            return False
    
    def enable_browser(self, headless: bool = False) -> bool:
        """启用内置浏览器"""
        logger.info("启用内置浏览器...")
        
        config = self.load_config()
        if not config:
            return False
        
        # 更新配置
        config["browser"] = {
            "enabled": True,
            "defaultProfile": "openclaw",
            "headless": headless,
            "noSandbox": False,
            "attachOnly": False,
            "executablePath": self.browser_config["browser"]["executablePath"]
        }
        
        # 保存配置
        if self.save_config(config):
            logger.info("✅ 内置浏览器已启用")
            logger.info(f"   Profile: openclaw")
            logger.info(f"   无头模式：{'是' if headless else '否'}")
            logger.info(f"   Chrome 路径：{self.browser_config['browser']['executablePath']}")
            
            # 验证配置
            if self.validate_config():
                logger.info("✅ 配置验证通过")
                # 询问是否重载
                print("\n是否立即重载 Gateway？(y/n): ", end='')
                try:
                    response = input().strip().lower()
                    if response == 'y':
                        self.reload_gateway()
                except:
                    pass
            else:
                logger.warning("⚠️ 配置验证失败，请检查")
            
            logger.info("\n⚠️ 如未自动重载，请手动运行：openclaw gateway restart")
            return True
        
        return False
    
    def disable_browser(self) -> bool:
        """禁用内置浏览器（恢复默认）"""
        logger.info("禁用内置浏览器，恢复默认配置...")
        
        config = self.load_config()
        if not config:
            return False
        
        # 移除 browser 配置
        if "browser" in config:
            del config["browser"]
        
        # 保存配置
        if self.save_config(config):
            logger.info("✅ 已恢复默认配置（Chrome 扩展模式）")
            
            # 询问是否重载
            print("\n是否立即重载 Gateway？(y/n): ", end='')
            try:
                response = input().strip().lower()
                if response == 'y':
                    self.reload_gateway()
            except:
                pass
            
            logger.info("\n⚠️ 如未自动重载，请手动运行：openclaw gateway restart")
            return True
        
        return False
    
    def apply_preset(self, preset: str) -> bool:
        """应用预设配置"""
        presets = {
            "dev": {
                "enabled": True,
                "defaultProfile": "openclaw",
                "headless": False,
                "noSandbox": True,
                "attachOnly": False
            },
            "privacy": {
                "enabled": True,
                "defaultProfile": "openclaw",
                "headless": True,
                "noSandbox": False,
                "attachOnly": True,
                "disableExtensions": True
            },
            "performance": {
                "enabled": True,
                "defaultProfile": "openclaw",
                "headless": True,
                "noSandbox": True,
                "disableGPU": True
            },
            "default": {
                "enabled": False,
                "defaultProfile": "chrome"
            }
        }
        
        if preset not in presets:
            logger.error(f"未知的预设：{preset}")
            logger.info(f"可用预设：{', '.join(presets.keys())}")
            return False
        
        logger.info(f"应用预设：{preset}")
        
        config = self.load_config()
        if not config:
            return False
        
        if preset == "default":
            # 恢复默认
            if "browser" in config:
                del config["browser"]
        else:
            config["browser"] = presets[preset]
        
        if self.save_config(config):
            logger.info(f"✅ 已应用预设：{preset}")
            return True
        
        return False
    
    def export_status(self, output_file: str) -> bool:
        """导出状态到文件"""
        status = self.get_status()
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ 状态已导出：{output_file}")
            return True
        except Exception as e:
            logger.error(f"导出失败：{e}")
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenClaw 浏览器切换工具')
    parser.add_argument('--enable', action='store_true', help='启用内置浏览器')
    parser.add_argument('--disable', action='store_true', help='禁用内置浏览器')
    parser.add_argument('--status', action='store_true', help='查看状态')
    parser.add_argument('--headless', action='store_true', help='启用无头模式')
    parser.add_argument('--validate', action='store_true', help='验证配置')
    parser.add_argument('--preset', type=str, choices=['dev', 'privacy', 'performance', 'default'],
                       help='应用预设配置')
    parser.add_argument('--export', type=str, help='导出状态到文件')
    parser.add_argument('--auto-detect', action='store_true', help='自动检测 Chrome 路径')
    
    args = parser.parse_args()
    
    toggle = BrowserToggle()
    
    if args.enable:
        success = toggle.enable_browser(headless=args.headless)
        sys.exit(0 if success else 1)
    elif args.disable:
        success = toggle.disable_browser()
        sys.exit(0 if success else 1)
    elif args.status:
        status = toggle.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        sys.exit(0)
    elif args.validate:
        success = toggle.validate_config()
        sys.exit(0 if success else 1)
    elif args.preset:
        success = toggle.apply_preset(args.preset)
        sys.exit(0 if success else 1)
    elif args.export:
        success = toggle.export_status(args.export)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
