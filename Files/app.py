import pybase64
import base64
import requests
import binascii
import os
import socket
import time
import json

TIMEOUT = 20  # HTTP 请求超时
SOCKET_TIMEOUT = 3  # 节点 TCP 测试超时（秒）

fixed_text = """#profile-title: base64:8J+GkyBHaXRodWIgfCBCYXJyeS1mYXIg8J+ltw==
#profile-update-interval: 1
#subscription-userinfo: upload=29; download=12; total=10737418240000000; expire=2546249531
#support-url: https://github.com/yd072/v2ray-configs
#profile-web-page-url: https://github.com/yd072/v2ray-configs
"""

def decode_base64(encoded):
    decoded = ""
    for encoding in ["utf-8", "iso-8859-1"]:
        try:
            decoded = pybase64.b64decode(encoded + b"=" * (-len(encoded) % 4)).decode(encoding)
            break
        except (UnicodeDecodeError, binascii.Error):
            pass
    return decoded

def decode_links(links):
    decoded_data = []
    for link in links:
        try:
            response = requests.get(link, timeout=TIMEOUT)
            encoded_bytes = response.content
            decoded_text = decode_base64(encoded_bytes)
            decoded_data.append(decoded_text)
        except requests.RequestException:
            pass
    return decoded_data

def decode_dir_links(dir_links):
    decoded_dir_links = []
    for link in dir_links:
        try:
            response = requests.get(link, timeout=TIMEOUT)
            decoded_text = response.text
            decoded_dir_links.append(decoded_text)
        except requests.RequestException:
            pass
    return decoded_dir_links

def filter_for_protocols(data, protocols):
    filtered_data = []
    for block in data:
        for line in block.splitlines():
            if any(protocol in line for protocol in protocols):
                filtered_data.append(line.strip())
    return filtered_data

def parse_vmess_config(vmess_url):
    if vmess_url.startswith("vmess://"):
        try:
            raw = vmess_url[8:]
            padded = raw + '=' * (-len(raw) % 4)
            decoded = base64.b64decode(padded).decode()
            return json.loads(decoded)
        except Exception:
            return None
    return None

def test_tcp_connect(host, port, timeout=SOCKET_TIMEOUT):
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except Exception:
        return False

def filter_alive_nodes(config_lines):
    alive = []
    for line in config_lines:
        if line.startswith("vmess://"):
            config = parse_vmess_config(line)
            if config and "add" in config and "port" in config:
                if test_tcp_connect(config["add"], config["port"]):
                    alive.append(line)
        else:
            continue  # 可扩展 vless/trojan 支持
    return alive

def ensure_directories_exist():
    output_folder = os.path.abspath(os.path.join(os.getcwd(), ".."))
    base64_folder = os.path.join(output_folder, "Base64")

    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(base64_folder, exist_ok=True)

    return output_folder, base64_folder

def main():
    output_folder, base64_folder = ensure_directories_exist()

    protocols = ["vmess"]  # 当前仅对 vmess 进行连接测试
    links = [
        "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
        "https://raw.githubusercontent.com/free18/v2ray/refs/heads/main/v.txt",
        "https://raw.githubusercontent.com/shaoyouvip/free/refs/heads/main/base64.txt"
    ]
    dir_links = [
        # 可选的明文节点链接
    ]

    decoded_links = decode_links(links)
    decoded_dir_links = decode_dir_links(dir_links)

    combined_data = decoded_links + decoded_dir_links
    merged_configs = filter_for_protocols(combined_data, protocols)
    merged_configs = filter_alive_nodes(merged_configs)  # 🔥 新增真连接过滤

    output_filename = os.path.join(output_folder, "All_Configs_Sub.txt")
    filename1 = os.path.join(output_folder, "All_Configs_base64_Sub.txt")

    if os.path.exists(output_filename):
        os.remove(output_filename)
    if os.path.exists(filename1):
        os.remove(filename1)

    for i in range(20):
        txt_file = os.path.join(output_folder, f"Sub{i}.txt")
        b64_file = os.path.join(base64_folder, f"Sub{i}_base64.txt")
        if os.path.exists(txt_file):
            os.remove(txt_file)
        if os.path.exists(b64_file):
            os.remove(b64_file)

    with open(output_filename, "w") as f:
        f.write(fixed_text)
        for config in merged_configs:
            f.write(config + "\n")

    with open(output_filename, "r") as f:
        lines = f.readlines()

    max_lines_per_file = 500
    num_lines = len(lines)
    num_files = (num_lines + max_lines_per_file - 1) // max_lines_per_file

    for i in range(num_files):
        profile_title = f"🆓 Git:Epodonios | Sub{i+1} 🔥"
        encoded_title = base64.b64encode(profile_title.encode()).decode()
        custom_fixed_text = f"""#profile-title: base64:{encoded_title}
#profile-update-interval: 1
#subscription-userinfo: upload=29; download=12; total=10737418240000000; expire=2546249531
#support-url: https://github.com/yd072/v2ray-configs
#profile-web-page-url: https://github.com/yd072/v2ray-configs
"""

        input_filename = os.path.join(output_folder, f"Sub{i + 1}.txt")
        with open(input_filename, "w") as f:
            f.write(custom_fixed_text)
            start_index = i * max_lines_per_file
            end_index = min((i + 1) * max_lines_per_file, num_lines)
            for line in lines[start_index:end_index]:
                f.write(line)

        with open(input_filename, "r") as input_file:
            config_data = input_file.read()
        
        output_filename = os.path.join(base64_folder, f"Sub{i + 1}_base64.txt")
        with open(output_filename, "w") as output_file:
            encoded_config = base64.b64encode(config_data.encode()).decode()
            output_file.write(encoded_config)

if __name__ == "__main__":
    main()
