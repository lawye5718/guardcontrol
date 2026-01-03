import hashlib
import getpass

def verify_password_hash():
    print("请让您的朋友输入解锁密码进行验证...")
    
    # 第一次输入
    password1 = getpass.getpass("请输入解锁密码第一次（输入时不会显示）: ")
    hash1 = hashlib.sha256(password1.encode()).hexdigest()
    
    print() # 空行
    # 第二次输入
    password2 = getpass.getpass("请输入解锁密码第二次（输入时不会显示）: ")
    hash2 = hashlib.sha256(password2.encode()).hexdigest()
    
    print(f"\n第一次输入生成的哈希值：{hash1}")
    print(f"第二次输入生成的哈希值：{hash2}")
    
    # 检查两次输入的hash值是否相同
    if hash1 == hash2:
        print("✅ 两次输入的哈希值一致")
        
        # 检查是否与提供的hash值匹配
        provided_hash = "9e7cae479aa6225c02e55646dc360bd980c47974f8ada384439f9137d834b197"
        if hash1 == provided_hash:
            print("✅ 生成的哈希值与提供的哈希值一致")
            print("现在可以更新guard_control.py中的密码哈希值")
            return hash1
        else:
            print("❌ 生成的哈希值与提供的哈希值不一致")
            print(f"提供的哈希值：{provided_hash}")
            return None
    else:
        print("❌ 两次输入的哈希值不一致，请重新输入")
        return None

if __name__ == "__main__":
    verify_password_hash()
