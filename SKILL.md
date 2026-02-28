# OpenClaw 内置浏览器 Skill

> 一键启用/禁用 OpenClaw 内置浏览器，无需手动修改配置文件

**版本：** v1.0  
**创建时间：** 2026-02-28  
**作者：** AI Assistant

---

## 🚀 快速使用

### 启用内置浏览器
```bash
openclaw skill run browser-toggle --enable
```

### 禁用内置浏览器（恢复默认）
```bash
openclaw skill run browser-toggle --disable
```

### 查看当前状态
```bash
openclaw skill run browser-toggle --status
```

---

## 📋 功能特性

- ✅ 一键切换内置浏览器模式
- ✅ 自动备份配置文件
- ✅ 失败自动恢复
- ✅ 支持 Linux/Windows/Mac
- ✅ 可视化/无头模式切换
- ✅ 配置验证

---

## 🔧 配置说明

### 内置浏览器模式
- **Profile:** `openclaw`
- **数据位置:** `~/.openclaw/browser/`
- **特点:** 独立空间，不访问个人浏览器

### 扩展模式（默认）
- **Profile:** `chrome`
- **需要:** Chrome 扩展
- **特点:** 使用个人 Chrome 浏览器

---

## 📖 详细文档

见 `README.md`

---

*Skill 版本：v1.0*  
*最后更新：2026-02-28*
