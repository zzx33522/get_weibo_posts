# 微博用户博文爬取工具

本脚本用于爬取指定微博用户的所有公开博文数据，并保存为Excel文件。

## 环境准备

### 1. 安装Python
- 访问 [Python官网](https://www.python.org/downloads/)，下载并安装Python 3.7或更高版本。
- 安装时务必勾选 **Add Python to PATH**。

### 2. 安装依赖库
打开命令行（Windows：`Win+R`输入`cmd`；Mac：打开终端），执行以下命令：
```bash
pip install requests pandas openpyxl selenium webdriver-manager