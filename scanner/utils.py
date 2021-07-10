from .windows import set_cpu_affinity
from datetime import datetime, timezone
from urllib.parse import urlsplit
import json
import socket
import threading
import time
import ctypes

class ChunkCounter:
    def __init__(self):
        self._count = 0
        self._lock = threading.Lock()
    
    def __add__(self, delta):
        with self._lock:
            self._count += delta
        return self
        
    def wait(self, interval):
        time.sleep(interval)
        with self._lock:
            count = self._count
            self._count = 0
            return count

def send_webhook(url, ssl_context, **kwargs):
    payload = json.dumps(kwargs, separators=(",", ":"))
    hostname, path = url.split("://", 1)[1].split("/", 1)
    sock = create_ssl_socket((hostname, 443), ssl_context=ssl_context)
    try:
        sock.send(f"POST /{path} HTTP/1.1\r\nHost: {hostname}\r\nContent-Length: {len(payload)}\r\nContent-Type: application/json\r\n\r\n{payload}".encode())
        conn.recv(1024 ** 2)
    finally:
        shutdown_socket(sock)

def make_embed(group_info):
    return dict(
        title="Found claimable group",
        url=f"https://www.roblox.com/groups/{group_info['id']}/--",
        fields=[
            dict(name="Group Id", value=group_info["id"]),
            dict(name="Group Name", value=group_info["name"]),
            dict(name="Group Members", value=group_info["memberCount"]),
            dict(name="Group Funds", value=f"R$ {group_info['funds']}" if group_info["funds"] is not None else "?")
        ],
        timestamp=datetime.now(timezone.utc).isoformat()
    )

def create_ssl_socket(addr, ssl_context, proxy_addr=None, timeout=5):
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect(proxy_addr or addr)

        if proxy_addr:
            sock.send(f"CONNECT {addr[0]}:{addr[1]} HTTP/1.1\r\n\r\n".encode())
            if not sock.recv(1024).startswith(b"HTTP/1.1 20"):
                raise ConnectionRefusedError(
                    "Proxy server did not return a correct response for tunnel request")

        sock = ssl_context.wrap_socket(sock, server_hostname=addr[0])
        return sock
    
    except:
        shutdown_socket(sock)
        raise

def shutdown_socket(sock):
    if not sock:
        return
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    sock.close()

def slice_list(lst, num, total):
    per = int(len(lst)/total)
    chunk = lst[per * num : per * (num + 1)]
    return chunk

def slice_range(r, num, total):
    per = int((r[1]-r[0]+1)/total)
    return (r[0] + num * per, (num + 1) * per)

def update_stats(text):
    ctypes.windll.kernel32.SetConsoleTitleW(text)