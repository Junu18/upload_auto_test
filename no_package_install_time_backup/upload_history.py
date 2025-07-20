# upload_history.py - 업로드 기록 관리 시스템
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class UploadHistoryManager:
    def __init__(self):
        self.history_file = "upload_history.json"
        self.ensure_history_file()
    
    def ensure_history_file(self):
        """기록 파일이 없으면 생성"""
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({"records": []}, f, ensure_ascii=False, indent=2)
    
    def add_record(self, file_path: str, action: str, status: str, 
                   commit_hash: str = "", error_message: str = "", 
                   file_size: int = 0, profile_name: str = ""):
        """업로드 기록 추가"""
        try:
            # 기존 기록 로드
            records = self.get_all_records()
            
            # 새 기록 생성
            new_record = {
                "id": self.generate_record_id(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "action": action,  # "upload", "update", "delete"
                "status": status,  # "success", "failed", "skipped"
                "commit_hash": commit_hash,
                "error_message": error_message,
                "file_size": file_size,
                "profile_name": profile_name
            }
            
            # 기록 추가 (최신순으로 정렬)
            records.insert(0, new_record)
            
            # 최대 1000개 기록만 유지
            if len(records) > 1000:
                records = records[:1000]
            
            # 파일에 저장
            self.save_records(records)
            return True
            
        except Exception as e:
            print(f"기록 추가 실패: {e}")
            return False
    
    def get_all_records(self) -> List[Dict]:
        """모든 기록 가져오기"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("records", [])
            return []
        except Exception as e:
            print(f"기록 로드 실패: {e}")
            return []
    
    def save_records(self, records: List[Dict]):
        """기록 저장"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({"records": records}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"기록 저장 실패: {e}")
    
    def generate_record_id(self) -> str:
        """고유 기록 ID 생성"""
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    
    def get_records_by_date(self, start_date: str, end_date: str) -> List[Dict]:
        """날짜 범위로 기록 필터링"""
        records = self.get_all_records()
        filtered = []
        
        for record in records:
            record_date = record.get("timestamp", "").split(" ")[0]
            if start_date <= record_date <= end_date:
                filtered.append(record)
        
        return filtered
    
    def get_records_by_status(self, status: str) -> List[Dict]:
        """상태별 기록 필터링"""
        records = self.get_all_records()
        return [r for r in records if r.get("status") == status]
    
    def get_records_by_profile(self, profile_name: str) -> List[Dict]:
        """프로필별 기록 필터링"""
        records = self.get_all_records()
        return [r for r in records if r.get("profile_name") == profile_name]
    
    def search_records(self, keyword: str) -> List[Dict]:
        """키워드로 기록 검색"""
        records = self.get_all_records()
        keyword = keyword.lower()
        
        filtered = []
        for record in records:
            if (keyword in record.get("file_name", "").lower() or 
                keyword in record.get("file_path", "").lower() or
                keyword in record.get("action", "").lower() or
                keyword in record.get("status", "").lower()):
                filtered.append(record)
        
        return filtered
    
    def clear_old_records(self, days: int = 30):
        """오래된 기록 삭제"""
        records = self.get_all_records()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered_records = []
        for record in records:
            try:
                record_time = datetime.strptime(record.get("timestamp", ""), "%Y-%m-%d %H:%M:%S")
                if record_time >= cutoff_date:
                    filtered_records.append(record)
            except:
                # 날짜 파싱 실패 시 유지
                filtered_records.append(record)
        
        self.save_records(filtered_records)
        return len(records) - len(filtered_records)
    
    def get_statistics(self) -> Dict:
        """업로드 통계 가져오기"""
        records = self.get_all_records()
        
        stats = {
            "total_records": len(records),
            "successful_uploads": 0,
            "failed_uploads": 0,
            "total_files_size": 0,
            "recent_activity": [],
            "top_files": {},
            "daily_counts": {}
        }
        
        for record in records:
            # 성공/실패 카운트
            if record.get("status") == "success":
                stats["successful_uploads"] += 1
            elif record.get("status") == "failed":
                stats["failed_uploads"] += 1
            
            # 파일 크기 합계
            stats["total_files_size"] += record.get("file_size", 0)
            
            # 파일별 업로드 횟수
            file_name = record.get("file_name", "")
            if file_name:
                stats["top_files"][file_name] = stats["top_files"].get(file_name, 0) + 1
            
            # 일별 업로드 수
            date = record.get("timestamp", "").split(" ")[0]
            if date:
                stats["daily_counts"][date] = stats["daily_counts"].get(date, 0) + 1
        
        # 최근 활동 (최근 5개)
        stats["recent_activity"] = records[:5]
        
        return stats