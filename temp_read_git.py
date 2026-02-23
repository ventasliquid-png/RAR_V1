import os, zlib

repo = r"C:\dev\RAR_V1"
branch = "rescate-cache-lupa"
file_path = "Conexion_Blindada.py"

with open(os.path.join(repo, ".git", "refs", "heads", branch), "r") as f:
    commit_hash = f.read().strip()

def read_object(sha):
    path = os.path.join(repo, ".git", "objects", sha[:2], sha[2:])
    with open(path, "rb") as f:
        return zlib.decompress(f.read())

commit_data = read_object(commit_hash).decode('utf-8')
tree_hash = commit_data.split("tree ")[1].split("\n")[0]

tree_data = read_object(tree_hash)

i = 0
file_sha = None
while i < len(tree_data):
    null_idx = tree_data.find(b'\x00', i)
    if null_idx == -1: break
    mode_name = tree_data[i:null_idx].decode('utf-8')
    name = mode_name.split(' ')[1]
    sha = tree_data[null_idx+1:null_idx+21].hex()
    if name == file_path:
        file_sha = sha
        break
    i = null_idx + 21

if file_sha:
    blob_data = read_object(file_sha)
    content = blob_data.split(b'\x00', 1)[1].decode('utf-8')
    with open(os.path.join(repo, "temp_cache_lupa.py"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Extracted to temp_cache_lupa.py")
else:
    print("File not found in tree")
