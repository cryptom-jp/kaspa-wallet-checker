#!/usr/bin/env python3
"""
Rusty-Kaspa gRPC接続テストスクリプト
ノードの接続確認と基本的なRPC呼び出しをテスト
"""
import sys
import grpc
sys.path.append('../proto')

import rpc_pb2
import messages_pb2
import messages_pb2_grpc

def test_connection():
    """gRPC接続テスト"""
    print("=== Kaspa gRPC接続テスト ===\n")
    
    # gRPCチャンネルの作成
    grpc_address = "localhost:16110"
    print(f"接続先: {grpc_address}")
    
    try:
        # 非セキュア接続（ローカルノード用）
        channel = grpc.insecure_channel(grpc_address)
        stub = messages_pb2_grpc.RPCStub(channel)
        
        # GetInfoリクエストの作成
        print("\n1. GetInfoRequest 送信中...")
        
        # KaspadRequestラッパーを作成
        kaspad_request = messages_pb2.KaspadRequest()
        kaspad_request.id = 1
        kaspad_request.getInfoRequest.CopyFrom(rpc_pb2.GetInfoRequestMessage())
        
        # 双方向ストリーミングでリクエスト送信
        def request_generator():
            yield kaspad_request
        
        responses = stub.MessageStream(request_generator())
        
        # レスポンスを取得
        for response in responses:
            if response.HasField('getInfoResponse'):
                info = response.getInfoResponse
                print("✅ 接続成功！")
                print(f"\nノード情報:")
                print(f"  サーバーバージョン: {info.serverVersion}")
                print(f"  P2P ID: {info.p2pId}")
                print(f"  同期状態: {'✅ 同期完了' if info.isSynced else '⏳ 同期中'}")
                print(f"  UTXO インデックス: {'有効' if info.isUtxoIndexed else '無効'}")
                print(f"  mempool サイズ: {info.mempoolSize}")
                print(f"  通知コマンド対応: {'はい' if info.hasNotifyCommand else 'いいえ'}")
                print(f"  メッセージID対応: {'はい' if info.hasMessageId else 'いいえ'}")
                
                # エラーチェック
                if info.error and info.error.message:
                    print(f"\n⚠️  エラー: {info.error.message}")
                    return False
                    
                break
        
        # 接続をクローズ
        channel.close()
        print("\n✅ テスト完了")
        return True
        
    except grpc.RpcError as e:
        print(f"\n❌ gRPCエラー: {e.code()}")
        print(f"   詳細: {e.details()}")
        return False
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {type(e).__name__}")
        print(f"   詳細: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_get_balance(address):
    """指定アドレスの残高取得テスト"""
    print(f"\n=== 残高取得テスト ===\n")
    print(f"アドレス: {address}")
    
    grpc_address = "localhost:16110"
    
    try:
        channel = grpc.insecure_channel(grpc_address)
        stub = messages_pb2_grpc.RPCStub(channel)
        
        # 残高リクエストの作成
        print("\n2. GetBalanceByAddressRequest 送信中...")
        
        kaspad_request = messages_pb2.KaspadRequest()
        kaspad_request.id = 2
        
        balance_request = rpc_pb2.GetBalanceByAddressRequestMessage()
        balance_request.address = address
        kaspad_request.getBalanceByAddressRequest.CopyFrom(balance_request)
        
        # リクエスト送信
        def request_generator():
            yield kaspad_request
        
        responses = stub.MessageStream(request_generator())
        
        # レスポンスを取得
        for response in responses:
            if response.HasField('getBalanceByAddressResponse'):
                balance_response = response.getBalanceByAddressResponse
                
                # エラーチェック
                if balance_response.error and balance_response.error.message:
                    print(f"\n⚠️  エラー: {balance_response.error.message}")
                    return False
                
                balance = balance_response.balance
                print("✅ 残高取得成功！")
                print(f"\n残高: {balance:,} sompi")
                print(f"残高（KAS）: {balance / 100000000:.8f} KAS")
                break
        
        channel.close()
        return True
        
    except grpc.RpcError as e:
        print(f"\n❌ gRPCエラー: {e.code()}")
        print(f"   詳細: {e.details()}")
        return False
    except Exception as e:
        print(f"\n❌ エラー: {type(e).__name__}")
        print(f"   詳細: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 基本接続テスト
    success = test_connection()
    
    if success and len(sys.argv) > 1:
        # コマンドライン引数でアドレスが指定された場合
        address = sys.argv[1]
        test_get_balance(address)
    elif success:
        print("\n💡 使い方: python grpc_test.py [kaspaアドレス]")
        print("   例: python grpc_test.py kaspa:qz7...")

