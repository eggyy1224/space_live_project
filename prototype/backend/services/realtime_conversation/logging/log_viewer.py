#!/usr/bin/env python3
"""
WebSocket 日誌查看工具
用於分析 realtime conversation 的日誌檔案。
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class LogViewer:
    """日誌查看器"""
    
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = Path(logs_dir)
        
        if not self.logs_dir.exists():
            print(f"❌ 日誌目錄不存在: {self.logs_dir}")
            return
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """列出所有會話日誌"""
        sessions = []
        
        for log_file in self.logs_dir.glob("session_*.log"):
            try:
                # 從檔名解析基本資訊
                parts = log_file.stem.split('_')
                if len(parts) >= 3:
                    date_part = parts[1]
                    time_part = parts[2] 
                    session_id = parts[3] if len(parts) > 3 else "unknown"
                    
                    # 解析時間戳
                    timestamp_str = f"{date_part}_{time_part}"
                    try:
                        timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    except ValueError:
                        timestamp = datetime.fromtimestamp(log_file.stat().st_mtime)
                    
                    # 獲取檔案大小
                    file_size = log_file.stat().st_size
                    
                    # 快速讀取檔案開頭來獲取會話資訊
                    session_info = self._extract_session_info(log_file)
                    
                    sessions.append({
                        "file_path": str(log_file),
                        "session_id": session_id,
                        "timestamp": timestamp,
                        "file_size": file_size,
                        "duration": session_info.get("duration", "unknown"),
                        "total_events": session_info.get("total_events", 0)
                    })
            except Exception as e:
                print(f"⚠️  無法解析日誌檔案 {log_file}: {e}")
        
        # 按時間排序
        sessions.sort(key=lambda x: x["timestamp"], reverse=True)
        return sessions
    
    def _extract_session_info(self, log_file: Path) -> Dict[str, Any]:
        """提取會話基本資訊"""
        info = {}
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # 統計事件數量
                event_count = 0
                duration = "unknown"
                
                for line in lines:
                    if "| " in line and " | " in line:
                        event_count += 1
                    elif "Session Duration:" in line:
                        duration = line.split("Session Duration:")[-1].strip()
                
                info["total_events"] = event_count
                info["duration"] = duration
                
        except Exception:
            pass
        
        return info
    
    def show_session_list(self):
        """顯示會話列表"""
        sessions = self.list_sessions()
        
        if not sessions:
            print("📭 沒有找到任何會話日誌")
            return
        
        print("📊 會話日誌列表")
        print("=" * 100)
        print(f"{'#':<3} {'Session ID':<10} {'時間':<20} {'檔案大小':<10} {'事件數量':<8} {'持續時間':<15}")
        print("-" * 100)
        
        for i, session in enumerate(sessions, 1):
            timestamp_str = session["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            file_size_str = f"{session['file_size'] / 1024:.1f}KB"
            
            print(f"{i:<3} {session['session_id']:<10} {timestamp_str:<20} {file_size_str:<10} {session['total_events']:<8} {session['duration']:<15}")
        
        print("-" * 100)
        print(f"總共 {len(sessions)} 個會話")
    
    def view_session(self, session_index: int = None, session_id: str = None, 
                    filter_category: str = None, filter_action: str = None, tail: int = None):
        """查看特定會話的詳細日誌"""
        sessions = self.list_sessions()
        
        if not sessions:
            print("📭 沒有找到任何會話日誌")
            return
        
        # 選擇會話
        target_session = None
        
        if session_index is not None:
            if 1 <= session_index <= len(sessions):
                target_session = sessions[session_index - 1]
            else:
                print(f"❌ 無效的會話索引: {session_index}")
                return
        elif session_id is not None:
            for session in sessions:
                if session["session_id"] == session_id:
                    target_session = session
                    break
            if not target_session:
                print(f"❌ 找不到會話 ID: {session_id}")
                return
        else:
            # 默認顯示最新的會話
            target_session = sessions[0]
        
        # 讀取並顯示日誌
        self._display_log_content(
            target_session["file_path"], 
            filter_category, 
            filter_action, 
            tail
        )
    
    def _display_log_content(self, file_path: str, filter_category: str = None, 
                           filter_action: str = None, tail: int = None):
        """顯示日誌內容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"📄 查看日誌: {file_path}")
            print("=" * 120)
            
            # 過濾日誌行
            filtered_lines = []
            
            for line in lines:
                # 跳過標題行
                if line.startswith("=") or line.startswith("🚀") or line.startswith("📊"):
                    if not filter_category and not filter_action:
                        filtered_lines.append(line)
                    continue
                
                # 解析日誌行
                if "| " in line and " | " in line:
                    try:
                        # 解析格式: [時間] 分類 | 動作 | JSON資料
                        parts = line.split(" | ", 2)
                        if len(parts) >= 3:
                            time_and_category = parts[0].strip()
                            action = parts[1].strip()
                            
                            # 提取分類
                            if "] " in time_and_category:
                                category = time_and_category.split("] ")[-1].strip()
                            else:
                                category = "unknown"
                            
                            # 應用過濾器
                            if filter_category and filter_category.upper() not in category.upper():
                                continue
                            if filter_action and filter_action.upper() not in action.upper():
                                continue
                            
                            filtered_lines.append(line)
                    except Exception:
                        # 如果解析失敗，顯示原始行
                        if not filter_category and not filter_action:
                            filtered_lines.append(line)
                else:
                    # 非日誌格式的行
                    if not filter_category and not filter_action:
                        filtered_lines.append(line)
            
            # 應用 tail 過濾
            if tail and tail > 0:
                # 只取最後 N 行的日誌事件
                event_lines = [line for line in filtered_lines if "| " in line and " | " in line]
                other_lines = [line for line in filtered_lines if not ("| " in line and " | " in line)]
                
                if len(event_lines) > tail:
                    filtered_lines = other_lines + event_lines[-tail:]
            
            # 顯示結果
            for line in filtered_lines:
                print(line.rstrip())
            
            # 顯示統計
            event_count = len([line for line in filtered_lines if "| " in line and " | " in line])
            print("\n" + "=" * 120)
            print(f"📊 顯示了 {event_count} 個事件")
            
            if filter_category or filter_action:
                filters = []
                if filter_category:
                    filters.append(f"分類={filter_category}")
                if filter_action:
                    filters.append(f"動作={filter_action}")
                print(f"🔍 過濾條件: {', '.join(filters)}")
            
        except Exception as e:
            print(f"❌ 讀取日誌失敗: {e}")
    
    def analyze_session(self, session_index: int = None, session_id: str = None):
        """分析會話統計資訊"""
        sessions = self.list_sessions()
        
        if not sessions:
            print("📭 沒有找到任何會話日誌")
            return
        
        # 選擇會話
        target_session = None
        
        if session_index is not None:
            if 1 <= session_index <= len(sessions):
                target_session = sessions[session_index - 1]
            else:
                print(f"❌ 無效的會話索引: {session_index}")
                return
        elif session_id is not None:
            for session in sessions:
                if session["session_id"] == session_id:
                    target_session = session
                    break
            if not target_session:
                print(f"❌ 找不到會話 ID: {session_id}")
                return
        else:
            # 默認分析最新的會話
            target_session = sessions[0]
        
        # 分析日誌
        self._analyze_log_file(target_session["file_path"])
    
    def extract_transcript(self, session_index: int = None, session_id: str = None):
        """提取 AI 回覆的完整轉錄內容"""
        sessions = self.list_sessions()
        
        if not sessions:
            print("📭 沒有找到任何會話日誌")
            return
        
        # 選擇會話
        target_session = None
        
        if session_index is not None:
            if 1 <= session_index <= len(sessions):
                target_session = sessions[session_index - 1]
            else:
                print(f"❌ 無效的會話索引: {session_index}")
                return
        elif session_id is not None:
            for session in sessions:
                if session["session_id"] == session_id:
                    target_session = session
                    break
            if not target_session:
                print(f"❌ 找不到會話 ID: {session_id}")
                return
        else:
            # 默認提取最新的會話
            target_session = sessions[0]
        
        # 提取轉錄內容
        self._extract_transcript_from_file(target_session["file_path"], target_session["session_id"])
    
    def _extract_transcript_from_file(self, file_path: str, session_id: str):
        """從日誌檔案中提取 AI 轉錄內容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"🎙️ 提取 AI 回覆內容: {session_id}")
            print("=" * 80)
            
            # 收集轉錄片段
            transcript_segments = []
            current_item = None
            current_text = ""
            
            for line in lines:
                if "RESPONSE_AUDIO_TRANSCRIPT_DELTA" in line:
                    try:
                        # 解析日誌行
                        parts = line.strip().split(' | ', 2)
                        if len(parts) < 3:
                            continue
                        
                        timestamp = parts[0].strip("[]")
                        data_json = parts[2]
                        data = json.loads(data_json)
                        
                        # 檢查是否有轉錄內容
                        if "transcript_delta" in data:
                            item_id = data.get("event_summary", {}).get("item_id")
                            delta_text = data["transcript_delta"]
                            
                            # 如果是新的對話項目，保存之前的內容
                            if item_id != current_item and current_text.strip():
                                transcript_segments.append({
                                    "item_id": current_item,
                                    "content": current_text.strip(),
                                    "timestamp": timestamp
                                })
                                current_text = ""
                            
                            current_item = item_id
                            current_text += delta_text
                            
                    except (json.JSONDecodeError, KeyError) as e:
                        continue
            
            # 保存最後一段內容
            if current_text.strip():
                transcript_segments.append({
                    "item_id": current_item,
                    "content": current_text.strip(),
                    "timestamp": "最後更新"
                })
            
            # 顯示結果
            if transcript_segments:
                print(f"🤖 找到 {len(transcript_segments)} 段 AI 回覆:")
                print()
                
                for i, segment in enumerate(transcript_segments, 1):
                    print(f"💬 回覆 #{i}")
                    print(f"🆔 Item ID: {segment['item_id']}")
                    print(f"⏰ 時間: {segment['timestamp']}")
                    print("-" * 60)
                    print(segment['content'])
                    print("-" * 60)
                    print()
            else:
                print("❌ 未找到 AI 回覆內容")
                print("💡 可能原因：")
                print("  1. 這是舊格式的日誌（需要更新的日誌記錄器）")
                print("  2. 會話中沒有 AI 回覆")
                print("  3. 日誌記錄不完整")
                
        except Exception as e:
            print(f"❌ 提取轉錄內容失敗: {e}")
    
    def _analyze_log_file(self, file_path: str):
        """分析日誌檔案統計"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"📊 分析日誌: {file_path}")
            print("=" * 80)
            
            # 統計各種事件
            categories = {}
            actions = {}
            errors = []
            function_calls = []
            audio_stats = {"chunks_sent": 0, "audio_processed": 0}
            
            for line in lines:
                if "| " in line and " | " in line:
                    try:
                        parts = line.split(" | ", 2)
                        if len(parts) >= 3:
                            time_and_category = parts[0].strip()
                            action = parts[1].strip()
                            data_json = parts[2].strip()
                            
                            # 提取分類
                            if "] " in time_and_category:
                                category = time_and_category.split("] ")[-1].strip()
                                timestamp = time_and_category.split("] ")[0] + "]"
                            else:
                                category = "unknown"
                                timestamp = time_and_category
                            
                            # 統計分類
                            categories[category] = categories.get(category, 0) + 1
                            actions[action] = actions.get(action, 0) + 1
                            
                            # 特殊事件處理
                            if category == "ERROR" or (category == "EVENT" and action == "ERROR"):
                                errors.append({
                                    "timestamp": timestamp,
                                    "action": action,
                                    "category": category,
                                    "data": data_json
                                })
                            elif category == "FUNCTION" and action == "EXECUTED":
                                try:
                                    data = json.loads(data_json)
                                    function_calls.append({
                                        "timestamp": timestamp,
                                        "function": data.get("function_name"),
                                        "success": data.get("success")
                                    })
                                except:
                                    pass
                            elif category == "AUDIO":
                                if action == "CHUNK_SENT":
                                    audio_stats["chunks_sent"] += 1
                                elif action == "PROCESSED":
                                    audio_stats["audio_processed"] += 1
                    
                    except Exception:
                        continue
            
            # 顯示統計結果
            print("📈 事件分類統計:")
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"  {category:>12}: {count:>4} 次")
            
            print("\n🎯 動作統計:")
            for action, count in sorted(actions.items(), key=lambda x: x[1], reverse=True):
                print(f"  {action:>20}: {count:>4} 次")
            
            print(f"\n🎵 音頻統計:")
            print(f"  發送音頻塊: {audio_stats['chunks_sent']:>4} 次")
            print(f"  處理音頻  : {audio_stats['audio_processed']:>4} 次")
            
            print(f"\n🔧 Function Call 統計:")
            if function_calls:
                func_stats = {}
                success_count = 0
                for call in function_calls:
                    func_name = call.get("function", "unknown")
                    func_stats[func_name] = func_stats.get(func_name, 0) + 1
                    if call.get("success"):
                        success_count += 1
                
                for func, count in sorted(func_stats.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {func:>20}: {count:>4} 次")
                print(f"  成功率: {success_count}/{len(function_calls)} ({success_count/len(function_calls)*100:.1f}%)")
            else:
                print("  無 Function Call")
            
            print(f"\n❌ 錯誤統計:")
            if errors:
                error_types = {}
                for error in errors:
                    error_types[error["action"]] = error_types.get(error["action"], 0) + 1
                
                for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {error_type:>20}: {count:>4} 次")
                
                print("\n最近的錯誤詳細資訊:")
                for error in errors[-3:]:  # 只顯示最近3個錯誤
                    print(f"  📅 {error['timestamp']} - {error['action']}")
                    try:
                        data = json.loads(error['data'])
                        if 'error_code' in data:
                            print(f"      錯誤代碼: {data.get('error_code', 'N/A')}")
                            print(f"      錯誤訊息: {data.get('error_message', 'N/A')}")
                            if data.get('error_param'):
                                print(f"      錯誤參數: {data.get('error_param')}")
                        elif 'message' in data:
                            print(f"      錯誤訊息: {data.get('message')}")
                        print()
                    except:
                        print(f"      原始數據: {error['data'][:100]}...")
                        print()
            else:
                print("  無錯誤 ✅")
            
        except Exception as e:
            print(f"❌ 分析失敗: {e}")


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="WebSocket 日誌查看工具")
    parser.add_argument("--logs-dir", default="logs", help="日誌目錄路徑")
    
    subparsers = parser.add_subparsers(dest="command", help="可用指令")
    
    # list 指令
    subparsers.add_parser("list", help="列出所有會話")
    
    # view 指令
    view_parser = subparsers.add_parser("view", help="查看會話詳細日誌")
    view_parser.add_argument("--session", type=int, help="會話索引 (從 list 指令獲取)")
    view_parser.add_argument("--session-id", type=str, help="會話 ID")
    view_parser.add_argument("--category", type=str, help="過濾分類 (例如: CONNECTION, AUDIO, FUNCTION)")
    view_parser.add_argument("--action", type=str, help="過濾動作 (例如: START, EXECUTED)")
    view_parser.add_argument("--tail", type=int, help="只顯示最後 N 個事件")
    
    # analyze 指令
    analyze_parser = subparsers.add_parser("analyze", help="分析會話統計")
    analyze_parser.add_argument("--session", type=int, help="會話索引")
    analyze_parser.add_argument("--session-id", type=str, help="會話 ID")
    
    # transcript 指令
    transcript_parser = subparsers.add_parser("transcript", help="提取AI回覆內容")
    transcript_parser.add_argument("--session", type=int, help="會話索引")
    transcript_parser.add_argument("--session-id", type=str, help="會話 ID")
    
    args = parser.parse_args()
    
    # 建立日誌查看器
    viewer = LogViewer(args.logs_dir)
    
    if args.command == "list":
        viewer.show_session_list()
    elif args.command == "view":
        viewer.view_session(
            session_index=args.session,
            session_id=args.session_id,
            filter_category=args.category,
            filter_action=args.action,
            tail=args.tail
        )
    elif args.command == "analyze":
        viewer.analyze_session(
            session_index=args.session,
            session_id=args.session_id
        )
    elif args.command == "transcript":
        viewer.extract_transcript(
            session_index=args.session,
            session_id=args.session_id
        )
    else:
        # 默認顯示會話列表
        viewer.show_session_list()
        print("\n💡 使用方法:")
        print("  python log_viewer.py list                      # 列出所有會話")
        print("  python log_viewer.py view --session 1          # 查看第1個會話")
        print("  python log_viewer.py view --category AUDIO     # 只看音頻事件")
        print("  python log_viewer.py view --tail 20            # 只看最後20個事件")
        print("  python log_viewer.py analyze --session 1       # 分析第1個會話")
        print("  python log_viewer.py transcript --session 1    # 提取AI回覆內容")


if __name__ == "__main__":
    main() 