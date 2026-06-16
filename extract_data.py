"""提取西南财经大学培养方案 ZIP 文件
用法: python extract_data.py

这个脚本会:
1. 从 /tmp 复制 ZIP 文件到项目的 tmp/ 目录
2. 以正确的中文编码提取所有 PDF 文件到 data/raw/swufe/
3. 显示提取到的文件列表
"""
import zipfile
import os
import shutil

# 路径配置
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ZIP_SRC = r"/tmp/swufe_training_plans.zip"
ZIP_DST = os.path.join(PROJECT_ROOT, "tmp", "swufe_training_plans.zip")
OUT_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "swufe")

def main():
    # 创建目录
    os.makedirs(os.path.dirname(ZIP_DST), exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    # 复制 ZIP
    if not os.path.exists(ZIP_SRC):
        print(f"错误: 找不到 ZIP 文件: {ZIP_SRC}")
        print("请先运行: curl -sL -o /tmp/swufe_training_plans.zip "
              "\"https://jwc.swufe.edu.cn/__local/D/73/5F/5B57901AAC6C1EF0E7E6716A7CB_84F36B39_E34A33.zip\"")
        return

    shutil.copy2(ZIP_SRC, ZIP_DST)
    print(f"ZIP 已复制到: {ZIP_DST}")

    # 提取
    with zipfile.ZipFile(ZIP_DST, "r") as z:
        count = 0
        for info in z.infolist():
            # ZIP 里的文件名是 CP437 编码，需要转成 GBK
            raw_bytes = info.filename.encode("cp437", errors="replace")
            try:
                decoded_name = raw_bytes.decode("gbk")
            except UnicodeDecodeError:
                decoded_name = info.filename

            if info.is_dir():
                os.makedirs(os.path.join(OUT_DIR, decoded_name), exist_ok=True)
            else:
                out_path = os.path.join(OUT_DIR, decoded_name)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with z.open(info.filename) as src, open(out_path, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                count += 1
                if count <= 20:
                    print(f"  [{count}] {decoded_name}")

    total = sum(1 for root, dirs, files in os.walk(OUT_DIR) for f in files)
    print(f"\n完成! 共提取 {total} 个文件到 {OUT_DIR}")

if __name__ == "__main__":
    main()
