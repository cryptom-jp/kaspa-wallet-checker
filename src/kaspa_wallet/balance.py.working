#!/usr/bin/env python3
"""
Kaspa残高取得モジュール（gRPC版 - 設定ファイル対応＋エラーハンドリング強化）
"""
import sys
import json
import grpc
import time
import logging
import yaml
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from functools import wraps

# protoファイルのインポート
sys.path.append('../../proto')
import rpc_pb2
import messages_pb2
import messages_pb2_grpc

# ===== 設定読み込み =====
def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """設定ファイルを読み込む"""
    try:
        config_file = Path(__file__).parent / config_path
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"警告: {config_path} が見つかりません。デフォルト設定を使用します。")
        return get_default_config()
    except Exception as e:
        print(f"設定ファイル読み込みエラー: {e}。デフォルト設定を使用します。")
        return get_default_config()

def get_default_config() -> Dict[str, Any]:
    """デフォルト設定を返す"""
    return {
        'grpc': {
            'address': 'localhost:16110',
            'timeout': 10,
            'max_retries': 3,
            'base_delay': 1.0,
            'max_receive_message_length': 52428800,
            'max_send_message_length': 52428800
        },
        'logging': {
            'level': 'INFO',
            'file': '../../logs/balance.log',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'console': True
        },
        'validation': {
            'min_address_length': 40,
            'allowed_prefixes': ['kaspa:', 'kaspatest:']
        }
    }

CONFIG = load_config()

# ===== ログ設定 =====
log_config = CONFIG['logging']
handlers = [logging.FileHandler(log_config['file'])]
if log_config.get('console', True):
    handlers.append(logging.StreamHandler())

logging.basicConfig(
    level=getattr(logging, log_config['level']),
    format=log_config['format'],
    handlers=handlers
)
logger = logging.getLogger(__name__)

# ===== カスタム例外クラス =====
class KaspaBalanceError(Exception):
    """基底例外クラス"""
    pass

class ConnectionError(KaspaBalanceError):
    """gRPC接続エラー"""
    pass

class TimeoutError(KaspaBalanceError):
    """タイムアウトエラー"""
    pass

class InvalidAddressError(KaspaBalanceError):
    """無効なアドレス形式"""
    pass

class NodeError(KaspaBalanceError):
    """ノードエラー"""
    pass

# ===== リトライデコレーター =====
def retry_with_backoff(max_attempts: int = None, base_delay: float = None):
    """指数バックオフでリトライするデコレーター"""
    if max_attempts is None:
        max_attempts = CONFIG['grpc']['max_retries']
    if base_delay is None:
        base_delay = CONFIG['grpc']['base_delay']
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except (grpc.RpcError, ConnectionError) as e:
                    if attempt == max_attempts:
                        logger.error(f"最大リトライ回数到達: {e}")
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"リトライ {attempt}/{max_attempts} - {delay}秒後に再試行: {e}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

# ===== アドレス検証 =====
def validate_address(address: str) -> Tuple[bool, Optional[str]]:
    """Kaspaアドレスの基本的な検証"""
    if not address or not isinstance(address, str):
        return False, "アドレスが空または文字列ではありません"
    
    address = address.strip()
    validation_config = CONFIG['validation']
    allowed_prefixes = validation_config['allowed_prefixes']
    min_length = validation_config['min_address_length']
    
    if not any(address.startswith(prefix) for prefix in allowed_prefixes):
        prefixes_str = 'または'.join(allowed_prefixes)
        return False, f"アドレスは{prefixes_str}で始まる必要があります"
    
    if len(address) < min_length:
        return False, f"アドレスが短すぎます（最低{min_length}文字必要）"
    
    return True, None

# ===== 残高取得本体 =====
@retry_with_backoff()
def get_balance_sompi(address: str) -> int:
    """指定されたKaspaアドレスの残高を取得（gRPC版）"""
    is_valid, error_msg = validate_address(address)
    if not is_valid:
        logger.error(f"アドレス検証失敗: {error_msg} - {address}")
        raise InvalidAddressError(error_msg)
    
    logger.info(f"残高取得開始: {address}")
    grpc_config = CONFIG['grpc']
    channel = None
    
    try:
        channel = grpc.insecure_channel(
            grpc_config['address'],
            options=[
                ('grpc.max_receive_message_length', grpc_config['max_receive_message_length']),
                ('grpc.max_send_message_length', grpc_config['max_send_message_length']),
            ]
        )
        stub = messages_pb2_grpc.RPCStub(channel)
        
        kaspad_request = messages_pb2.KaspadRequest()
        kaspad_request.id = 1
        
        balance_request = rpc_pb2.GetBalanceByAddressRequestMessage()
        balance_request.address = address
        kaspad_request.getBalanceByAddressRequest.CopyFrom(balance_request)
        
        def request_generator():
            yield kaspad_request
        
        responses = stub.MessageStream(
            request_generator(),
            timeout=grpc_config['timeout']
        )
        
        for response in responses:
            if response.HasField('getBalanceByAddressResponse'):
                balance_response = response.getBalanceByAddressResponse
                if balance_response.error and balance_response.error.message:
                    error_msg = balance_response.error.message
                    logger.error(f"ノードエラー: {error_msg}")
                    raise NodeError(f"Node error: {error_msg}")
                
                balance = balance_response.balance
                logger.info(f"残高取得成功: {address} = {balance} sompi")
                if channel:
                    channel.close()
                return balance
        
        logger.error("ノードからレスポンスがありません")
        if channel:
            channel.close()
        raise NodeError("No response received from node")
        
    except grpc.RpcError as e:
        if channel:
            channel.close()
        if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            logger.error(f"タイムアウト: {e.details()}")
            raise TimeoutError(f"Request timeout: {e.details()}")
        elif e.code() == grpc.StatusCode.UNAVAILABLE:
            logger.error(f"接続不可: {e.details()}")
            raise ConnectionError(f"Node unavailable: {e.details()}")
        else:
            logger.error(f"gRPCエラー: {e.code()} - {e.details()}")
            raise ConnectionError(f"gRPC error: {e.code()} - {e.details()}")
    except Exception as e:
        if channel:
            channel.close()
        logger.error(f"予期しないエラー: {str(e)}")
        raise

# ===== CLIエントリーポイント =====
def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "address argument is required"}))
        logger.error("引数不足: アドレスが指定されていません")
        sys.exit(1)
    
    address = sys.argv[1].strip()
    
    try:
        balance_sompi = get_balance_sompi(address)
        balance_kas = balance_sompi / 10**8
        
        output = {
            "address": address,
            "balance_sompi": balance_sompi,
            "balance_kas": balance_kas,
            "status": "success"
        }
        print(json.dumps(output))
        logger.info(f"処理完了: {address}")
        
    except InvalidAddressError as e:
        print(json.dumps({
            "error": "invalid_address",
            "message": str(e),
            "address": address
        }))
        sys.exit(1)
    except TimeoutError as e:
        print(json.dumps({
            "error": "timeout",
            "message": str(e),
            "address": address
        }))
        sys.exit(1)
    except ConnectionError as e:
        print(json.dumps({
            "error": "connection_failed",
            "message": str(e),
            "address": address
        }))
        sys.exit(1)
    except NodeError as e:
        print(json.dumps({
            "error": "node_error",
            "message": str(e),
            "address": address
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "error": "unknown_error",
            "message": str(e),
            "address": address
        }))
        logger.exception("予期しないエラー")
        sys.exit(1)

if __name__ == "__main__":
    main()
