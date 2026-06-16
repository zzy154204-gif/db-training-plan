"""修复 ZIP 提取后的中文文件名乱码"""
import os
import shutil
import zipfile

PROJECT_ROOT = r"C:\Users\张宗元\db-project"
TMP_DIR = r"/tmp/db-data/swufe"
OUT_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "swufe")

def fix_filenames():
    """将乱码文件名通过编码转换恢复为中文"""
    renamed = 0
    for root, dirs, files in os.walk(TMP_DIR, topdown=False):
        for name in files + dirs:
            old_path = os.path.join(root, name)
            try:
                # 将 CP437 编码的乱码转回 GBK
                fixed = name.encode("cp437", errors="replace").decode("gbk", errors="replace")
            except:
                fixed = name
            if fixed != name:
                new_path = os.path.join(root, fixed)
                try:
                    os.rename(old_path, new_path)
                    renamed += 1
                except:
                    pass
    print(f"修复了 {renamed} 个文件名")

def copy_to_project():
    """把修复后的文件复制到项目目录"""
    if os.path.exists(OUT_DIR):
        shutil.rmtree(OUT_DIR)

    # 找到最深层的目录（实际 PDF 所在位置）
    for root, dirs, files in os.walk(TMP_DIR):
        if files:
            rel = os.path.relpath(root, TMP_DIR)
            # 只取深层目录名（去掉重复的父目录前缀）
            parts = rel.split(os.sep)
            # 找到 "25级本科人才培养方案" 那一层
            target_parts = []
            for p in parts:
                if "2025" in p or "25" in p or "培养" in p:
                    continue  # 跳过顶层重复目录
                target_parts.append(p)

            if target_parts:
                subdir = os.path.join(*target_parts)
            else:
                subdir = ""

            for f in files:
                src = os.path.join(root, f)
                dst_dir = os.path.join(OUT_DIR, subdir)
                os.makedirs(dst_dir, exist_ok=True)
                shutil.copy2(src, dst_dir)

    print(f"文件已复制到 {OUT_DIR}")

def list_structure():
    """列出最终的文件结构"""
    print("\n=== 文件结构 ===")
    for root, dirs, files in os.walk(OUT_DIR):
        level = root.replace(OUT_DIR, "").count(os.sep)
        indent = "  " * level
        folder = os.path.basename(root)
        if folder:
            print(f"{indent}{folder}/")
        sub_indent = "  " * (level + 1)
        for f in files:
            print(f"{sub_indent}{f}")

if __name__ == "__main__":
    fix_filenames()
    copy_to_project()
    list_structure()
