import os

def generate_tree(root_dir, indent=""):
    tree = ""
    for item in sorted(os.listdir(root_dir)):
        path = os.path.join(root_dir, item)
        if os.path.isdir(path):
            tree += f"{indent}├── /{item}/\n"
            tree += generate_tree(path, indent + "│   ")
        else:
            tree += f"{indent}├── {item}\n"
    return tree

def save_structure_to_md(root_dir, output_file="project_structure.md"):
    header = f"# 📁 {os.path.basename(root_dir)} — ディレクトリ構造メモ\n\n```plaintext\n"
    footer = "```\n"
    tree = generate_tree(root_dir)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(header + tree + footer)
    print(f"✅ 保存完了: {output_file}")

# 使用例（ルートディレクトリを指定）
if __name__ == "__main__":
    root_directory = "C:\\Users\\0602JP\\Documents\\training\\training\\sqlite\\analyze"  # 必要に応じてパスを変更
    save_structure_to_md(root_directory)