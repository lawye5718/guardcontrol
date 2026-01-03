import hashlib

def generate_hash():
    print("请让您的朋友输入解锁密码：")
    # 注意：这里不会显示输入的密码字符，以保护隐私
    import getpass
    password = getpass.getpass("请输入解锁密码（输入时不会显示）: ")
    
    # 计算SHA256哈希值
    hash_value = hashlib.sha256(password.encode()).hexdigest()
    
    print(f"\n生成的SHA256哈希值：")
    print(hash_value)
    
    return hash_value

if __name__ == "__main__":
    generate_hash()
