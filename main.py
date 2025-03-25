import asyncio
import multiprocessing
from listen_new_direct_full_details import listen_for_new_tokens
from listen_to_raydium_migration import listen_for_events

def run_new_tokens_listener():
    """运行监听新代币的进程"""
    print("开始监听新代币...")
    asyncio.run(listen_for_new_tokens())

def run_raydium_migration_listener():
    """运行监听 Raydium 迁移的进程"""
    print("开始监听 Raydium 迁移事件...")
    asyncio.run(listen_for_events())

if __name__ == "__main__":
    # 创建两个进程
    new_tokens_process = multiprocessing.Process(
        target=run_new_tokens_listener,
        name="NewTokensListener"
    )
    
    raydium_migration_process = multiprocessing.Process(
        target=run_raydium_migration_listener,
        name="RaydiumMigrationListener"
    )
    
    # 启动进程
    try:
        print("正在启动监听进程...")
        new_tokens_process.start()
        raydium_migration_process.start()
        
        print(f"新代币监听进程 PID: {new_tokens_process.pid}")
        print(f"Raydium 迁移监听进程 PID: {raydium_migration_process.pid}")
        
        # 等待进程结束（在这种情况下，它们应该不会自然结束）
        new_tokens_process.join()
        raydium_migration_process.join()
    except KeyboardInterrupt:
        print("\n检测到中断，正在优雅地关闭进程...")
        # 正常终止进程
        new_tokens_process.terminate()
        raydium_migration_process.terminate()
        
        # 等待进程结束
        new_tokens_process.join()
        raydium_migration_process.join()
        print("所有进程已关闭")
    except Exception as e:
        print(f"发生错误: {e}")
        # 确保进程被终止
        if new_tokens_process.is_alive():
            new_tokens_process.terminate()
        if raydium_migration_process.is_alive():
            raydium_migration_process.terminate()