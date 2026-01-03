import hashlib
import getpass

def test_hash_generation():
    print("测试hash生成功能...")
    pwd = getpass.getpass("请输入测试密码（输入时不会显示）: ")
    hash_value = hashlib.sha256(pwd.encode()).hexdigest()
    print(f"生成的SHA256哈希值：{hash_value}")
    return hash_value

if __name__ == "__main__":
    test_hash_generation()
