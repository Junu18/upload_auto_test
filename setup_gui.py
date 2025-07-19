# setup_gui.py - UI 개선 버전 (완료 버튼 강조)
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
from env_generate import EnvGenerator

class GitHubAutoUploadSetup:
    def __init__(self):
        self.root = tk.Tk()
        self.env_generator = EnvGenerator()
        self.upload_mode = tk.StringVar(value="hybrid")
        self.repeat_option = tk.StringVar(value="daily")
        
        # 시간 설정용 StringVar 추가
        self.hour_var = tk.StringVar(value="14")
        self.minute_var = tk.StringVar(value="30")
        
        self.setup_ui()
        
        # 기존 설정 불러오기
        self.load_existing_config()
    
    def setup_ui(self):
        self.root.title("🚀 GitHub 자동 업로드 설정")
        self.root.geometry("650x950")  # 🔧 높이 증가
        self.root.resizable(False, False)
        
        # 메인 프레임
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # 제목
        title_label = tk.Label(main_frame, text="🚀 GitHub 자동 업로드 설정", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 기본 설정
        self.create_basic_settings(main_frame)
        
        # 업로드 모드
        self.create_upload_mode_section(main_frame)
        
        # 시간 설정
        self.create_time_section(main_frame)
        
        # 🔧 상태 표시를 버튼 위로 이동
        self.status_label = tk.Label(main_frame, text="설정을 입력해주세요.", fg="blue", font=("Arial", 10))
        self.status_label.pack(pady=10)
        
        # 🔧 버튼 (더 강조되게 수정)
        self.create_button_section(main_frame)
    
    def create_basic_settings(self, parent):
        # GitHub 토큰
        tk.Label(parent, text="🔑 GitHub Personal Access Token:", 
                font=("Arial", 10, "bold")).pack(anchor='w', pady=(10, 5))
        self.token_entry = tk.Entry(parent, width=60, show="*", font=("Arial", 10))
        self.token_entry.pack(anchor='w', pady=(0, 5))
        
        # 사용자명
        tk.Label(parent, text="👤 GitHub 사용자명:", 
                font=("Arial", 10, "bold")).pack(anchor='w', pady=(10, 5))
        self.username_entry = tk.Entry(parent, width=30, font=("Arial", 10))
        self.username_entry.pack(anchor='w', pady=(0, 5))
        
        # 저장소명
        tk.Label(parent, text="📂 저장소 이름:", 
                font=("Arial", 10, "bold")).pack(anchor='w', pady=(10, 5))
        self.repo_entry = tk.Entry(parent, width=30, font=("Arial", 10))
        self.repo_entry.pack(anchor='w', pady=(0, 5))
        
        # 폴더 경로
        tk.Label(parent, text="📁 감시할 폴더 경로:", 
                font=("Arial", 10, "bold")).pack(anchor='w', pady=(10, 5))
        folder_frame = tk.Frame(parent)
        folder_frame.pack(anchor='w', fill='x', pady=(0, 5))
        self.folder_entry = tk.Entry(folder_frame, width=50, font=("Arial", 10))
        self.folder_entry.pack(side='left', padx=(0, 10))
        tk.Button(folder_frame, text="📁 찾아보기", 
                 command=self.browse_folder).pack(side='left')
    
    def create_upload_mode_section(self, parent):
        mode_frame = tk.LabelFrame(parent, text="⏰ 업로드 모드 설정", 
                                  font=("Arial", 10, "bold"), padx=10, pady=10)
        mode_frame.pack(fill='x', pady=20)
        
        tk.Radiobutton(mode_frame, text="🔄 실시간 감시 (파일 넣으면 즉시 업로드)", 
                      variable=self.upload_mode, value="realtime",
                      command=self.on_mode_change).pack(anchor='w', pady=5)
        
        tk.Radiobutton(mode_frame, text="⏰ 시간 예약 (지정 시간에만 업로드)", 
                      variable=self.upload_mode, value="schedule",
                      command=self.on_mode_change).pack(anchor='w', pady=5)
        
        tk.Radiobutton(mode_frame, text="🔄⏰ 혼합 모드 (실시간 + 예약)", 
                      variable=self.upload_mode, value="hybrid",
                      command=self.on_mode_change).pack(anchor='w', pady=5)
    
    def create_time_section(self, parent):
        self.time_frame = tk.LabelFrame(parent, text="🕐 업로드 시간 설정", 
                                       font=("Arial", 10, "bold"), padx=10, pady=10)
        self.time_frame.pack(fill='x', pady=10)
        
        # 시간 입력
        time_input_frame = tk.Frame(self.time_frame)
        time_input_frame.pack(anchor='w', pady=10)
        
        tk.Label(time_input_frame, text="시간:", font=("Arial", 10)).pack(side='left')
        
        # textvariable 추가
        self.hour_spinbox = tk.Spinbox(time_input_frame, from_=0, to=23, width=5, 
                                      format="%02.0f", font=("Arial", 12),
                                      textvariable=self.hour_var)
        self.hour_spinbox.pack(side='left', padx=5)
        
        tk.Label(time_input_frame, text=":", font=("Arial", 12, "bold")).pack(side='left')
        
        # textvariable 추가
        self.minute_spinbox = tk.Spinbox(time_input_frame, from_=0, to=59, width=5, 
                                        format="%02.0f", font=("Arial", 12),
                                        textvariable=self.minute_var)
        self.minute_spinbox.pack(side='left', padx=5)
        
        # 반복 설정
        repeat_frame = tk.Frame(self.time_frame)
        repeat_frame.pack(anchor='w', pady=10)
        
        tk.Label(repeat_frame, text="반복 설정:", font=("Arial", 10)).pack(side='left')
        repeat_combo = ttk.Combobox(repeat_frame, textvariable=self.repeat_option, 
                                   values=["daily", "weekdays", "weekends"], 
                                   state="readonly", width=15)
        repeat_combo.pack(side='left', padx=10)
    
    def load_existing_config(self):
        """기존 .env 파일이 있으면 설정을 불러옵니다"""
        if os.path.exists('.env'):
            try:
                from dotenv import load_dotenv
                load_dotenv()
                
                # 기본 설정 불러오기
                token = os.getenv('GITHUB_TOKEN', '')
                username = os.getenv('GITHUB_USERNAME', '')
                repo = os.getenv('GITHUB_REPO', '')
                folder = os.getenv('WATCH_FOLDER', '')
                mode = os.getenv('UPLOAD_MODE', 'hybrid')
                repeat = os.getenv('REPEAT_OPTION', 'daily')
                
                # 시간 설정 불러오기
                upload_time = os.getenv('UPLOAD_TIME', '14:30')
                try:
                    hour, minute = upload_time.split(':')
                    self.hour_var.set(f"{int(hour):02d}")
                    self.minute_var.set(f"{int(minute):02d}")
                except:
                    pass
                
                # Entry 필드에 값 설정
                if token:
                    self.token_entry.insert(0, token)
                if username:
                    self.username_entry.insert(0, username)
                if repo:
                    self.repo_entry.insert(0, repo)
                if folder:
                    self.folder_entry.insert(0, folder)
                
                # 모드 및 반복 설정
                self.upload_mode.set(mode)
                self.repeat_option.set(repeat)
                
                # 모드에 따른 시간 설정 활성화/비활성화
                self.on_mode_change()
                
                self.status_label.config(text="기존 설정을 불러왔습니다.", fg="green")
                
            except Exception as e:
                print(f"설정 불러오기 실패: {e}")
                pass
    
    def on_mode_change(self):
        if self.upload_mode.get() == "realtime":
            self.disable_time_settings()
        else:
            self.enable_time_settings()
    
    def enable_time_settings(self):
        for widget in self.time_frame.winfo_children():
            self.enable_widget_recursive(widget)
    
    def disable_time_settings(self):
        for widget in self.time_frame.winfo_children():
            self.disable_widget_recursive(widget)
    
    def enable_widget_recursive(self, widget):
        try:
            widget.configure(state='normal')
        except:
            pass
        for child in widget.winfo_children():
            self.enable_widget_recursive(child)
    
    def disable_widget_recursive(self, widget):
        try:
            widget.configure(state='disabled')
        except:
            pass
        for child in widget.winfo_children():
            self.disable_widget_recursive(child)
    
    def browse_folder(self):
        folder_path = filedialog.askdirectory(title="감시할 폴더를 선택하세요")
        if folder_path:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_path)
    
    # 🔧 버튼 섹션 개선 - 더 눈에 띄게
    def create_button_section(self, parent):
        # 구분선 추가
        separator = tk.Frame(parent, height=2, bg="lightgray")
        separator.pack(fill='x', pady=20)
        
        # 안내 텍스트 추가
        guide_label = tk.Label(parent, text="📋 모든 설정을 완료한 후 '완료' 버튼을 눌러주세요!", 
                              font=("Arial", 11, "bold"), fg="blue")
        guide_label.pack(pady=10)
        
        button_frame = tk.Frame(parent)
        button_frame.pack(pady=20)
        
        # 🔧 버튼들을 더 크고 눈에 띄게 수정
        tk.Button(button_frame, text="❌ 취소", width=12, height=2,
                 font=("Arial", 10),
                 command=self.cancel_setup).pack(side='left', padx=15)
        
        tk.Button(button_frame, text="🔍 연결 테스트", width=12, height=2,
                 font=("Arial", 10), bg="lightblue",
                 command=self.test_connection).pack(side='left', padx=15)
        
        # 🔧 완료 버튼을 더 강조
        complete_btn = tk.Button(button_frame, text="✅ 완료", width=12, height=2,
                                bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                                command=self.create_env)
        complete_btn.pack(side='left', padx=15)
        
        # 🔧 완료 버튼 설명 추가
        complete_info = tk.Label(parent, text="완료 버튼 클릭 → .env 파일 생성 → main_upload.py 실행 가능", 
                                font=("Arial", 9), fg="gray")
        complete_info.pack(pady=5)
    
    # 🔧 취소 기능 개선
    def cancel_setup(self):
        result = messagebox.askyesno("설정 취소", "설정을 취소하고 창을 닫으시겠습니까?")
        if result:
            self.root.quit()
    
    def test_connection(self):
        token = self.token_entry.get().strip()
        username = self.username_entry.get().strip()
        repo_name = self.repo_entry.get().strip()
        
        if not all([token, username, repo_name]):
            messagebox.showwarning("입력 오류", "토큰, 사용자명, 저장소명을 모두 입력해주세요.")
            return
        
        self.status_label.config(text="🔍 연결 테스트 중...", fg="orange")
        self.root.update()
        
        # 토큰 검증
        token_valid, token_msg = self.env_generator.validate_token(token)
        if not token_valid:
            self.status_label.config(text="❌ 토큰 오류", fg="red")
            messagebox.showerror("토큰 오류", token_msg)
            return
        
        # 저장소 검증
        repo_valid, repo_msg = self.env_generator.validate_repository(token, username, repo_name)
        if not repo_valid:
            self.status_label.config(text="❌ 저장소 오류", fg="red")
            messagebox.showerror("저장소 오류", repo_msg)
            return
        
        self.status_label.config(text="✅ 연결 테스트 성공!", fg="green")
        messagebox.showinfo("테스트 성공", "GitHub 연결이 정상적으로 확인되었습니다!")
    
    # 🔧 완료 기능 개선
    def create_env(self):
        print("\n🔄 환경설정 완료 버튼 클릭됨!")  # 디버그용
        
        # 입력값 가져오기
        token = self.token_entry.get().strip()
        username = self.username_entry.get().strip()
        repo_name = self.repo_entry.get().strip()
        folder_path = self.folder_entry.get().strip()
        
        upload_mode = self.upload_mode.get()
        schedule_hour = None
        schedule_minute = None
        repeat_option = self.repeat_option.get()
        
        print(f"📋 수집된 정보:")
        print(f"   토큰: {'있음' if token else '없음'}")
        print(f"   사용자명: {username}")
        print(f"   저장소: {repo_name}")
        print(f"   폴더: {folder_path}")
        print(f"   모드: {upload_mode}")
        
        if upload_mode in ["schedule", "hybrid"]:
            try:
                schedule_hour = int(self.hour_var.get())
                schedule_minute = int(self.minute_var.get())
                print(f"   시간: {schedule_hour:02d}:{schedule_minute:02d}")
            except ValueError:
                messagebox.showerror("오류", "시간과 분은 숫자여야 합니다.")
                return
        
        # 🔧 입력값 검증 강화
        if not token:
            messagebox.showwarning("입력 오류", "GitHub 토큰을 입력해주세요.")
            self.token_entry.focus()
            return
        if not username:
            messagebox.showwarning("입력 오류", "GitHub 사용자명을 입력해주세요.")
            self.username_entry.focus()
            return
        if not repo_name:
            messagebox.showwarning("입력 오류", "저장소 이름을 입력해주세요.")
            self.repo_entry.focus()
            return
        if not folder_path:
            messagebox.showwarning("입력 오류", "감시할 폴더 경로를 선택해주세요.")
            self.folder_entry.focus()
            return
        
        self.status_label.config(text="🔄 .env 파일 생성 중...", fg="orange")
        self.root.update()
        
        # .env 파일 생성
        success, message = self.env_generator.create_env_file_with_schedule(
            token, username, repo_name, folder_path, upload_mode, 
            schedule_hour, schedule_minute, repeat_option
        )
        
        if success:
            self.status_label.config(text="✅ .env 파일 생성 완료!", fg="green")
            result = messagebox.showinfo("🎉 설정 완료!", 
                                        f"{message}\n\n"
                                        f"✅ .env 파일이 생성되었습니다!\n"
                                        f"🚀 이제 main_gui.py에서 '업로드 시작'을 클릭하세요!")
            print("✅ 환경설정 완료!")
            self.root.quit()
        else:
            self.status_label.config(text="❌ .env 파일 생성 실패", fg="red")
            messagebox.showerror("오류", message)
            print(f"❌ 오류: {message}")

if __name__ == "__main__":
    print("🚀 GitHub 자동 업로드 설정 GUI 시작...")
    app = GitHubAutoUploadSetup()
    app.root.mainloop()
    print("👋 설정 GUI 종료")