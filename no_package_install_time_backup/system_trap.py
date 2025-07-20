import tkinter as tk
from tkinter import messagebox
import pystray
from PIL import Image, ImageDraw
import threading
import subprocess
import os
import sys
import psutil
import time
from pathlib import Path

# 기존 클래스들 import
from env_generate import EnvGenerator
from upload_history import UploadHistoryManager

class GitHubAutoUploadTray:
    def __init__(self):
        self.env_generator = EnvGenerator()
        self.history_manager = UploadHistoryManager()
        
        # 업로드 프로세스 관리
        self.upload_process = None
        self.upload_pid_file = "upload_process.pid"
        self.is_upload_running = False
        
        # 현재 활성 프로필
        self.current_profile = ""
        
        # 트레이 아이콘 및 메뉴
        self.icon = None
        
        print("🔥 GitHub 자동 업로드 트레이 시스템 초기화 완료")
    
    def create_image(self):
        """트레이 아이콘 이미지 생성"""
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # GitHub 스타일 아이콘
        draw.ellipse([8, 8, 56, 56], fill='black')
        draw.ellipse([16, 16, 48, 48], fill='white')
        draw.ellipse([24, 24, 40, 40], fill='black')
        
        # 상태에 따른 색상 변경
        if self.is_upload_running:
            draw.rectangle([50, 8, 58, 16], fill='green')  # 실행 중 표시
        
        return image
    
    def update_icon_status(self):
        """아이콘 상태 업데이트"""
        if self.icon:
            self.icon.icon = self.create_image()
    
    def check_upload_process_status(self):
        """업로드 프로세스 상태 확인"""
        try:
            if os.path.exists(self.upload_pid_file):
                with open(self.upload_pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                if psutil.pid_exists(pid):
                    try:
                        process = psutil.Process(pid)
                        if 'python' in process.name().lower():
                            self.is_upload_running = True
                            self.upload_process = type('MockProcess', (), {'pid': pid, 'poll': lambda: None})()
                            return True
                    except psutil.NoSuchProcess:
                        pass
                
                os.remove(self.upload_pid_file)
            
            self.is_upload_running = False
            return False
            
        except Exception as e:
            print(f"프로세스 상태 확인 실패: {e}")
            self.is_upload_running = False
            return False
    
    def get_current_profile_info(self):
        """현재 활성 프로필 정보 가져오기"""
        try:
            from dotenv import load_dotenv
            load_dotenv(override=True)
            
            username = os.getenv('GITHUB_USERNAME', 'Unknown')
            repo = os.getenv('GITHUB_REPO', 'Unknown')
            self.current_profile = f"{username}/{repo}"
            return self.current_profile
        except:
            return "설정 없음"
    
    # 메뉴 액션들
    def toggle_upload(self, icon, item):
        """업로드 시작/중지 토글"""
        if self.is_upload_running:
            self.stop_upload()
        else:
            self.start_upload()
        
        # 메뉴 업데이트
        icon.menu = self.create_menu()
        self.update_icon_status()
    
    def start_upload(self):
        """업로드 시작"""
        try:
            if self.is_upload_running:
                self.show_notification("업로드가 이미 실행 중입니다!")
                return
            
            # 설정 확인
            if not os.path.exists('.env'):
                self.show_notification("환경설정이 필요합니다!")
                self.open_settings(None, None)
                return
            
            # 업로드 프로세스 시작
            self.upload_process = subprocess.Popen(
                [sys.executable, 'main_upload.py'],
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            # PID 파일 저장
            with open(self.upload_pid_file, 'w') as f:
                f.write(str(self.upload_process.pid))
            
            self.is_upload_running = True
            
            profile_info = self.get_current_profile_info()
            self.show_notification(f"업로드 시작!\n프로필: {profile_info}")
            
        except Exception as e:
            self.show_notification(f"업로드 시작 실패: {e}")
    
    def stop_upload(self):
        """업로드 중지"""
        try:
            if self.upload_process and hasattr(self.upload_process, 'pid'):
                try:
                    parent = psutil.Process(self.upload_process.pid)
                    children = parent.children(recursive=True)
                    
                    # 자식 프로세스들 종료
                    for child in children:
                        try:
                            child.terminate()
                        except psutil.NoSuchProcess:
                            pass
                    
                    # 부모 프로세스 종료
                    parent.terminate()
                    
                    # 강제 종료 (필요시)
                    gone, still_alive = psutil.wait_procs([parent] + children, timeout=3)
                    for p in still_alive:
                        try:
                            p.kill()
                        except psutil.NoSuchProcess:
                            pass
                    
                except psutil.NoSuchProcess:
                    pass
            
            # PID 파일 삭제
            if os.path.exists(self.upload_pid_file):
                os.remove(self.upload_pid_file)
            
            self.upload_process = None
            self.is_upload_running = False
            
            self.show_notification("업로드가 중지되었습니다!")
            
        except Exception as e:
            self.show_notification(f"업로드 중지 실패: {e}")
    
    def create_profile_submenu(self):
        """프로필 선택 서브메뉴 생성"""
        profiles = self.env_generator.get_all_profiles()
        
        if not profiles:
            return pystray.Menu(
                pystray.MenuItem("저장된 프로필이 없습니다", lambda: None, enabled=False)
            )
        
        profile_items = []
        for profile in profiles:
            profile_items.append(
                pystray.MenuItem(f"📋 {profile}", 
                               lambda p=profile: self.switch_profile(p))
            )
        
        return pystray.Menu(*profile_items)
    
    def switch_profile(self, profile_name):
        """프로필 전환"""
        try:
            # 업로드 중이면 중지
            if self.is_upload_running:
                self.stop_upload()
                time.sleep(1)
            
            success, message = self.env_generator.copy_profile_to_current_env(profile_name)
            
            if success:
                self.current_profile = profile_name
                self.show_notification(f"프로필 전환: {profile_name}")
            else:
                self.show_notification(f"프로필 전환 실패: {message}")
        except Exception as e:
            self.show_notification(f"프로필 전환 오류: {e}")
    
    def open_main_gui(self, icon, item):
        """메인 GUI 열기"""
        try:
            subprocess.Popen([sys.executable, 'main_gui.py'])
        except Exception as e:
            self.show_notification(f"메인 화면 열기 실패: {e}")
    
    def open_settings(self, icon, item):
        """환경설정 열기"""
        try:
            subprocess.Popen([sys.executable, 'setup_gui.py'])
        except Exception as e:
            self.show_notification(f"환경설정 열기 실패: {e}")
    
    def open_baekjoon(self, icon, item):
        """백준 문제 풀기 열기"""
        try:
            subprocess.Popen([sys.executable, 'baekjoon_gui.py'])
        except Exception as e:
            self.show_notification(f"백준 문제 열기 실패: {e}")
    
    def show_recent_history(self, icon, item):
        """최근 업로드 기록 표시"""
        try:
            records = self.history_manager.get_all_records()[:5]
            
            if not records:
                self.show_notification("업로드 기록이 없습니다!")
                return
            
            history_text = "📊 최근 업로드 기록:\n\n"
            for record in records:
                status_icon = "✅" if record.get('status') == 'success' else "❌"
                time_str = record.get('timestamp', '').split(' ')[1][:5]  # HH:MM
                file_name = record.get('file_name', '')
                history_text += f"{status_icon} {time_str} {file_name}\n"
            
            self.show_notification(history_text)
        except Exception as e:
            self.show_notification(f"기록 조회 실패: {e}")
    
    def show_upload_stats(self, icon, item):
        """업로드 통계 표시"""
        try:
            stats = self.history_manager.get_statistics()
            
            total = stats['total_records']
            success = stats['successful_uploads']
            failed = stats['failed_uploads']
            success_rate = (success / max(total, 1)) * 100
            
            stats_text = f"""📈 업로드 통계:

📄 총 기록: {total}개
✅ 성공: {success}개
❌ 실패: {failed}개
📊 성공률: {success_rate:.1f}%"""
            
            self.show_notification(stats_text)
        except Exception as e:
            self.show_notification(f"통계 조회 실패: {e}")
    
    def create_menu(self):
        """트레이 메뉴 생성"""
        # 현재 상태 확인
        upload_text = "⏹️ 업로드 중지" if self.is_upload_running else "▶️ 업로드 시작"
        
        return pystray.Menu(
            # 제목
            pystray.MenuItem("🚀 GitHub 자동 업로드", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            
            # 업로드 제어
            pystray.MenuItem(upload_text, self.toggle_upload),
            
            # 프로필 관리
            pystray.MenuItem("📋 프로필 선택", self.create_profile_submenu()),
            
            pystray.Menu.SEPARATOR,
            
            # GUI 열기
            pystray.MenuItem("📋 메인 화면", self.open_main_gui),
            pystray.MenuItem("⚙️ 환경설정", self.open_settings),
            pystray.MenuItem("📚 백준 문제", self.open_baekjoon),
            
            pystray.Menu.SEPARATOR,
            
            # 기록 및 통계
            pystray.MenuItem("📊 최근 기록", self.show_recent_history),
            pystray.MenuItem("📈 업로드 통계", self.show_upload_stats),
            
            pystray.Menu.SEPARATOR,
            
            # 종료
            pystray.MenuItem("❌ 완전 종료", self.quit_app)
        )
    
    def show_notification(self, message):
        """트레이 알림 표시"""
        if self.icon:
            try:
                # Windows 알림
                if sys.platform == "win32":
                    self.icon.notify(message, "GitHub 자동 업로드")
                else:
                    print(f"📢 {message}")
            except:
                print(f"📢 {message}")
    
    def quit_app(self, icon, item):
        """앱 완전 종료"""
        try:
            # 업로드 중지
            if self.is_upload_running:
                self.stop_upload()
            
            # 트레이 아이콘 종료
            icon.stop()
        except Exception as e:
            print(f"종료 중 오류: {e}")
            icon.stop()
    
    def start_monitoring(self):
        """백그라운드 모니터링 시작"""
        def monitor():
            while True:
                try:
                    # 프로세스 상태 체크
                    old_status = self.is_upload_running
                    new_status = self.check_upload_process_status()
                    
                    # 상태 변경 시 아이콘 업데이트
                    if old_status != new_status:
                        self.update_icon_status()
                        if self.icon:
                            self.icon.menu = self.create_menu()
                    
                    time.sleep(5)  # 5초마다 체크
                    
                except Exception as e:
                    print(f"모니터링 오류: {e}")
                    time.sleep(10)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def run(self):
        """트레이 앱 실행"""
        # 초기 상태 확인
        self.check_upload_process_status()
        self.get_current_profile_info()
        
        # 트레이 아이콘 생성
        image = self.create_image()
        menu = self.create_menu()
        
        self.icon = pystray.Icon(
            "GitHub Auto Upload",
            image,
            f"GitHub 자동 업로드\n프로필: {self.current_profile}",
            menu
        )
        
        # 백그라운드 모니터링 시작
        self.start_monitoring()
        
        print("🔥 시스템 트레이에서 실행 중...")
        print("💡 트레이 아이콘을 우클릭하여 메뉴를 확인하세요")
        print("📢 알림으로 상태 변화를 확인할 수 있습니다")
        
        # 초기 알림
        self.show_notification("트레이에서 실행 시작!\n우클릭으로 메뉴를 확인하세요.")
        
        # 트레이 아이콘 실행
        self.icon.run()

if __name__ == "__main__":
    try:
        print("🚀 GitHub 자동 업로드 트레이 시스템 시작...")
        app = GitHubAutoUploadTray()
        app.run()
    except Exception as e:
        print(f"💥 트레이 앱 실행 오류: {e}")
        input("Press Enter to exit...")