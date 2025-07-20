# main_gui.py - 업로드 시작/중지 토글 기능 추가된 완전 버전
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os
import sys
import psutil  # 🔧 프로세스 관리용 추가
import threading
import time
from dotenv import load_dotenv
from env_generate import EnvGenerator

class GitHubAutoUploadMain:
    def __init__(self):
        self.root = tk.Tk()
        self.env_generator = EnvGenerator()
        self.current_profile = tk.StringVar()
        
        # 🔧 업로드 프로세스 관리 변수들
        self.upload_process = None
        self.upload_pid_file = "upload_process.pid"
        self.is_upload_running = False
        
        self.setup_ui()
        self.load_profiles()
        self.update_status()
        self.check_upload_process()  # 🔧 시작 시 업로드 프로세스 상태 체크
        self.start_process_monitor()  # 🔧 프로세스 모니터링 시작
        
    def setup_ui(self):
        self.root.title("🚀 GitHub 자동 업로드")
        self.root.geometry("500x720")  # 높이 약간 증가
        self.root.resizable(False, False)
        
        # 메인 프레임
        main_frame = tk.Frame(self.root, padx=30, pady=30)
        main_frame.pack(fill='both', expand=True)
        
        # 제목
        title_label = tk.Label(main_frame, text="🚀 GitHub Auto Upload", 
                              font=("Arial", 20, "bold"), fg="navy")
        title_label.pack(pady=(0, 20))
        
        # 프로필 선택 섹션
        self.create_profile_section(main_frame)
        
        # 상태 표시 프레임
        self.create_status_frame(main_frame)
        
        # 기능 버튼들
        self.create_function_buttons(main_frame)
        
        # 종료 버튼
        self.create_exit_button(main_frame)
    
    def create_profile_section(self, parent):
        profile_frame = tk.LabelFrame(parent, text="🏷️ 프로필 선택", 
                                     font=("Arial", 12, "bold"), 
                                     padx=20, pady=15)
        profile_frame.pack(fill='x', pady=(0, 20))
        
        # 프로필 선택 영역
        selection_frame = tk.Frame(profile_frame)
        selection_frame.pack(fill='x', pady=5)
        
        tk.Label(selection_frame, text="현재 프로필:", 
                font=("Arial", 11, "bold")).pack(side='left')
        
        self.profile_combobox = ttk.Combobox(selection_frame, 
                                           textvariable=self.current_profile,
                                           state="readonly", 
                                           width=20, 
                                           font=("Arial", 11))
        self.profile_combobox.pack(side='left', padx=(10, 10))
        self.profile_combobox.bind('<<ComboboxSelected>>', self.on_profile_change)
        
        # 새로고침 버튼
        refresh_profiles_btn = tk.Button(selection_frame, text="🔄", 
                                       command=self.load_profiles,
                                       font=("Arial", 10), width=3)
        refresh_profiles_btn.pack(side='left', padx=5)
        
        # 프로필 정보 표시
        self.profile_info_label = tk.Label(profile_frame, 
                                          text="프로필을 선택하세요", 
                                          font=("Arial", 10), 
                                          fg="gray")
        self.profile_info_label.pack(anchor='w', pady=(10, 0))
    
    def load_profiles(self):
        """프로필 목록을 로드하여 Combobox에 설정"""
        try:
            profiles = self.env_generator.get_all_profiles()
            
            if profiles:
                self.profile_combobox['values'] = profiles
                
                # 현재 선택된 프로필이 없거나 목록에 없으면 첫 번째 프로필 선택
                current = self.current_profile.get()
                if not current or current not in profiles:
                    self.current_profile.set(profiles[0])
                    self.on_profile_change()
                
                self.profile_info_label.config(
                    text=f"사용 가능한 프로필: {len(profiles)}개", 
                    fg="darkgreen"
                )
            else:
                self.profile_combobox['values'] = []
                self.current_profile.set("")
                self.profile_info_label.config(
                    text="저장된 프로필이 없습니다. 환경설정에서 프로필을 생성하세요.", 
                    fg="orange"
                )
            
            print(f"📋 프로필 목록 로드: {profiles}")
            
        except Exception as e:
            print(f"❌ 프로필 로드 실패: {e}")
            self.profile_info_label.config(
                text="프로필 로드 실패", 
                fg="red"
            )
    
    def on_profile_change(self, event=None):
        """프로필이 변경될 때 호출되는 함수"""
        selected_profile = self.current_profile.get()
        if not selected_profile:
            return
        
        try:
            print(f"🔄 프로필 전환: {selected_profile}")
            
            # 선택한 프로필을 현재 .env로 복사
            success, message = self.env_generator.copy_profile_to_current_env(selected_profile)
            
            if success:
                print(f"✅ 프로필 전환 성공: {message}")
                
                # 프로필 정보 업데이트
                profile_info = self.env_generator.get_profile_info(selected_profile)
                if profile_info:
                    repo = profile_info.get('GITHUB_REPO', 'Unknown')
                    username = profile_info.get('GITHUB_USERNAME', 'Unknown')
                    self.profile_info_label.config(
                        text=f"활성 프로필: {selected_profile} → {username}/{repo}", 
                        fg="darkblue"
                    )
                
                # 상태 정보 업데이트
                self.update_status()
                
            else:
                print(f"❌ 프로필 전환 실패: {message}")
                messagebox.showerror("프로필 전환 실패", message)
                
        except Exception as e:
            print(f"❌ 프로필 변경 중 오류: {e}")
            messagebox.showerror("오류", f"프로필 변경 중 오류가 발생했습니다: {e}")
    
    def create_status_frame(self, parent):
        status_frame = tk.LabelFrame(parent, text="📊 현재 상태", 
                                    font=("Arial", 12, "bold"), 
                                    padx=20, pady=15)
        status_frame.pack(fill='x', pady=(0, 20))
        
        self.status_label = tk.Label(status_frame, text="⚙️ 설정 확인 중...", 
                                    font=("Arial", 11), fg="orange")
        self.status_label.pack(anchor='w', pady=5)
        
        self.folder_label = tk.Label(status_frame, text="📁 감시 폴더: 확인 중...", 
                                    font=("Arial", 10), fg="gray")
        self.folder_label.pack(anchor='w', pady=2)
        
        self.repo_label = tk.Label(status_frame, text="📂 저장소: 확인 중...", 
                                  font=("Arial", 10), fg="gray")
        self.repo_label.pack(anchor='w', pady=2)
        
        self.mode_label = tk.Label(status_frame, text="🔧 업로드 모드: 확인 중...", 
                                  font=("Arial", 10), fg="gray")
        self.mode_label.pack(anchor='w', pady=2)
        
        # 🔧 업로드 상태 표시 추가
        self.upload_status_label = tk.Label(status_frame, text="🚀 업로드 상태: 중지됨", 
                                           font=("Arial", 10, "bold"), fg="red")
        self.upload_status_label.pack(anchor='w', pady=2)
    
    def create_function_buttons(self, parent):
        button_frame = tk.Frame(parent)
        button_frame.pack(pady=20)
        
        # 첫 번째 줄
        first_row = tk.Frame(button_frame)
        first_row.pack(pady=10)
        
        baekjoon_btn = tk.Button(first_row, text="📚\n백준 문제\n풀기", 
                                width=12, height=4,
                                font=("Arial", 11, "bold"),
                                bg="lightblue", fg="navy",
                                command=self.open_baekjoon)
        baekjoon_btn.pack(side='left', padx=20)
        
        setup_btn = tk.Button(first_row, text="⚙️\n환경설정", 
                             width=12, height=4,
                             font=("Arial", 11, "bold"),
                             bg="lightgreen", fg="darkgreen",
                             command=self.open_setup)
        setup_btn.pack(side='left', padx=20)
        
        # 두 번째 줄
        second_row = tk.Frame(button_frame)
        second_row.pack(pady=10)
        
        # 🔧 업로드 시작/중지 토글 버튼
        self.upload_btn = tk.Button(second_row, text="🚀\n업로드\n시작", 
                                   width=12, height=4,
                                   font=("Arial", 11, "bold"),
                                   bg="orange", fg="white",
                                   command=self.toggle_upload)
        self.upload_btn.pack(side='left', padx=20)
        
        history_btn = tk.Button(second_row, text="📊\n업로드\n기록", 
                               width=12, height=4,
                               font=("Arial", 11, "bold"),
                               bg="lightgray", fg="black",
                               command=self.show_history)
        history_btn.pack(side='left', padx=20)
        
        # 상태 새로고침 버튼
        refresh_btn = tk.Button(button_frame, text="🔄 상태 새로고침", 
                               width=20, height=1,
                               font=("Arial", 10),
                               bg="lightcyan", fg="darkblue",
                               command=self.update_status)
        refresh_btn.pack(pady=10)
    
    def create_exit_button(self, parent):
        exit_btn = tk.Button(parent, text="종료", width=10, height=2,
                            font=("Arial", 11),
                            command=self.on_exit)
        exit_btn.pack(pady=20)
    
    # 🔧 업로드 시작/중지 토글 기능
    def toggle_upload(self):
        """업로드 시작/중지 토글"""
        if self.is_upload_running:
            self.stop_upload()
        else:
            self.start_upload()
    
    def start_upload(self):
        """업로드 프로그램 시작"""
        try:
            # 이미 실행 중이면 중복 실행 방지
            if self.is_upload_running:
                messagebox.showwarning("경고", "업로드가 이미 실행 중입니다!")
                return
            
            # 프로세스 시작
            self.upload_process = subprocess.Popen([sys.executable, 'main_upload.py'])
            
            # PID 저장
            with open(self.upload_pid_file, 'w') as f:
                f.write(str(self.upload_process.pid))
            
            # 상태 업데이트
            self.is_upload_running = True
            self.update_upload_button()
            
            # 성공 메시지
            current_profile = self.current_profile.get()
            if current_profile:
                message_text = f"GitHub 자동 업로드가 시작되었습니다!\n\n현재 프로필: {current_profile}\n콘솔 창에서 업로드 상태를 확인할 수 있습니다."
            else:
                message_text = "GitHub 자동 업로드가 시작되었습니다!\n\n콘솔 창에서 업로드 상태를 확인할 수 있습니다."
            
            messagebox.showinfo("시작", message_text)
            print(f"✅ 업로드 프로세스 시작됨 (PID: {self.upload_process.pid})")
            
        except FileNotFoundError:
            messagebox.showerror("오류", "main_upload.py 파일을 찾을 수 없습니다!")
        except Exception as e:
            messagebox.showerror("오류", f"업로드 프로그램을 시작할 수 없습니다: {e}")
            self.is_upload_running = False
            self.update_upload_button()
    
    def stop_upload(self):
        """업로드 프로그램 중지"""
        try:
            if self.upload_process and self.upload_process.poll() is None:
                # 프로세스가 아직 실행 중인 경우
                try:
                    # psutil로 프로세스 트리 전체 종료 (자식 프로세스도 함께)
                    parent = psutil.Process(self.upload_process.pid)
                    children = parent.children(recursive=True)
                    
                    # 자식 프로세스들 먼저 종료
                    for child in children:
                        try:
                            child.terminate()
                        except psutil.NoSuchProcess:
                            pass
                    
                    # 부모 프로세스 종료
                    parent.terminate()
                    
                    # 3초 대기 후 강제 종료
                    gone, still_alive = psutil.wait_procs([parent] + children, timeout=3)
                    for p in still_alive:
                        try:
                            p.kill()
                        except psutil.NoSuchProcess:
                            pass
                    
                    print(f"✅ 업로드 프로세스 종료됨 (PID: {self.upload_process.pid})")
                    
                except psutil.NoSuchProcess:
                    print("ℹ️  프로세스가 이미 종료되었습니다")
                except Exception as e:
                    print(f"⚠️  프로세스 종료 중 오류: {e}")
                    # psutil 실패 시 기본 방법 사용
                    self.upload_process.terminate()
            
            # PID 파일 삭제
            if os.path.exists(self.upload_pid_file):
                os.remove(self.upload_pid_file)
            
            # 상태 업데이트
            self.upload_process = None
            self.is_upload_running = False
            self.update_upload_button()
            
            messagebox.showinfo("중지", "GitHub 자동 업로드가 중지되었습니다!")
            
        except Exception as e:
            messagebox.showerror("오류", f"업로드 프로그램을 중지할 수 없습니다: {e}")
            print(f"❌ 업로드 중지 실패: {e}")
    
    # 🔧 업로드 버튼 상태 업데이트
    def update_upload_button(self):
        """업로드 버튼 상태 업데이트"""
        if self.is_upload_running:
            self.upload_btn.config(
                text="⏹️\n업로드\n중지",
                bg="red",
                fg="white"
            )
            self.upload_status_label.config(
                text="🚀 업로드 상태: 실행 중",
                fg="green"
            )
        else:
            self.upload_btn.config(
                text="🚀\n업로드\n시작",
                bg="orange",
                fg="white"
            )
            self.upload_status_label.config(
                text="🚀 업로드 상태: 중지됨",
                fg="red"
            )
    
    # 🔧 업로드 프로세스 상태 체크
    def check_upload_process(self):
        """시작 시 업로드 프로세스 상태 체크"""
        try:
            if os.path.exists(self.upload_pid_file):
                with open(self.upload_pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # 프로세스가 실제로 실행 중인지 확인
                if psutil.pid_exists(pid):
                    try:
                        process = psutil.Process(pid)
                        # 프로세스 이름 확인 (python 프로세스인지)
                        if 'python' in process.name().lower():
                            self.is_upload_running = True
                            self.upload_process = subprocess.Popen([], shell=False)  # 더미 객체
                            self.upload_process.pid = pid
                            print(f"ℹ️  기존 업로드 프로세스 발견 (PID: {pid})")
                        else:
                            # 다른 프로세스가 같은 PID를 사용 중
                            os.remove(self.upload_pid_file)
                    except psutil.NoSuchProcess:
                        os.remove(self.upload_pid_file)
                else:
                    # 프로세스가 종료됨
                    os.remove(self.upload_pid_file)
            
            self.update_upload_button()
            
        except Exception as e:
            print(f"⚠️  프로세스 상태 체크 실패: {e}")
            self.is_upload_running = False
            self.update_upload_button()
    
    # 🔧 주기적 프로세스 모니터링
    def start_process_monitor(self):
        """프로세스 상태 주기적 모니터링"""
        def monitor():
            while True:
                try:
                    if self.is_upload_running and self.upload_process:
                        # 프로세스가 종료되었는지 확인
                        if self.upload_process.poll() is not None:
                            # 프로세스가 종료됨
                            self.is_upload_running = False
                            self.upload_process = None
                            
                            # PID 파일 삭제
                            if os.path.exists(self.upload_pid_file):
                                os.remove(self.upload_pid_file)
                            
                            # UI 업데이트 (메인 스레드에서 실행)
                            self.root.after(0, self.update_upload_button)
                            print("ℹ️  업로드 프로세스가 종료되어 버튼 상태를 업데이트했습니다")
                    
                    time.sleep(2)  # 2초마다 체크
                    
                except Exception as e:
                    print(f"⚠️  프로세스 모니터링 오류: {e}")
                    time.sleep(5)  # 오류 시 5초 대기
        
        # 데몬 스레드로 시작
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def update_status(self):
        """현재 설정 상태 확인"""
        try:
            print("🔄 상태 업데이트 중...")
            
            if os.path.exists('.env'):
                load_dotenv(override=True)
                
                token = os.getenv('GITHUB_TOKEN')
                username = os.getenv('GITHUB_USERNAME')
                repo = os.getenv('GITHUB_REPO')
                folder = os.getenv('WATCH_FOLDER')
                mode = os.getenv('UPLOAD_MODE', 'realtime')
                
                print(f"📋 환경변수 체크:")
                print(f"   토큰: {'있음' if token else '없음'}")
                print(f"   사용자명: {username}")
                print(f"   저장소: {repo}")
                print(f"   폴더: {folder}")
                print(f"   모드: {mode}")
                
                if all([token, username, repo, folder]):
                    current_profile = self.current_profile.get()
                    if current_profile:
                        self.status_label.config(
                            text=f"✅ 설정 완료 - 업로드 준비됨 (프로필: {current_profile})", 
                            fg="green"
                        )
                    else:
                        self.status_label.config(text="✅ 설정 완료 - 업로드 준비됨", fg="green")
                    
                    self.folder_label.config(text=f"📁 감시 폴더: {folder}", fg="black")
                    self.repo_label.config(text=f"📂 저장소: {username}/{repo}", fg="black")
                    
                    mode_text = {
                        "realtime": "실시간 감시",
                        "schedule": "시간 예약", 
                        "hybrid": "실시간 + 예약"
                    }
                    self.mode_label.config(text=f"🔧 업로드 모드: {mode_text.get(mode, mode)}", fg="black")
                    
                    # 업로드 실행 중이 아닐 때만 버튼 활성화
                    if not self.is_upload_running:
                        self.upload_btn.config(state='normal')
                    
                    print("✅ 설정 완료!")
                else:
                    self.status_label.config(text="⚠️ 설정 불완전 - 환경설정 필요", fg="orange")
                    if not self.is_upload_running:
                        self.upload_btn.config(state='disabled', bg="gray")
                    print("⚠️ 설정 불완전")
            else:
                self.status_label.config(text="❌ 설정 없음 - 환경설정 필요", fg="red")
                self.folder_label.config(text="📁 감시 폴더: 설정되지 않음", fg="gray")
                self.repo_label.config(text="📂 저장소: 설정되지 않음", fg="gray")
                self.mode_label.config(text="🔧 업로드 모드: 설정되지 않음", fg="gray")
                if not self.is_upload_running:
                    self.upload_btn.config(state='disabled', bg="gray")
                print("❌ .env 파일 없음")
                
        except Exception as e:
            self.status_label.config(text="❌ 설정 오류 발생", fg="red")
            if not self.is_upload_running:
                self.upload_btn.config(state='disabled', bg="gray")
            print(f"❌ 에러: {e}")
    
    def open_baekjoon(self):
        """백준 문제 풀기 창 열기"""
        try:
            subprocess.Popen([sys.executable, 'baekjoon_gui.py'])
        except FileNotFoundError:
            messagebox.showerror("오류", "baekjoon_gui.py 파일을 찾을 수 없습니다!")
        except Exception as e:
            messagebox.showerror("오류", f"백준 문제 창을 열 수 없습니다: {e}")
    
    def open_setup(self):
        """환경설정 창 열기"""
        try:
            process = subprocess.Popen([sys.executable, 'setup_gui.py'])
            
            def wait_and_update():
                process.wait()
                self.root.after(100, self.load_profiles)
                self.root.after(200, self.update_status)
            
            threading.Thread(target=wait_and_update, daemon=True).start()
            
        except FileNotFoundError:
            messagebox.showerror("오류", "setup_gui.py 파일을 찾을 수 없습니다!")
        except Exception as e:
            messagebox.showerror("오류", f"환경설정 창을 열 수 없습니다: {e}")
    
    def show_history(self):
        messagebox.showinfo("개발 중", "업로드 기록 기능은 개발 중입니다!")
    
    # 🔧 종료 시 업로드 프로세스 정리
    def on_exit(self):
        """프로그램 종료 시 처리"""
        if self.is_upload_running:
            result = messagebox.askyesno(
                "종료 확인", 
                "업로드가 실행 중입니다.\n업로드를 중지하고 종료하시겠습니까?"
            )
            if result:
                self.stop_upload()
                self.root.quit()
        else:
            self.root.quit()

if __name__ == "__main__":
    print("🚀 GitHub 자동 업로드 메인 GUI 시작...")
    app = GitHubAutoUploadMain()
    app.root.mainloop()
    print("👋 메인 GUI 종료")