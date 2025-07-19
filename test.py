# import ttkbootstrap as ttk
# from ttkbootstrap.dialogs import dialogs
# import tkinter as tk
# from tkinter import filedialog, scrolledtext
# import threading
# import time
# import requests
# import base64
# import os
# import json
# import queue
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
# import webbrowser


# # --- 설정 관리 기능 ---
# CONFIG_FILE = "config.json"

# def save_settings(settings):
#     try:
#         with open(CONFIG_FILE, "w", encoding="utf-8") as f:
#             json.dump(settings, f, indent=4)
#         return True
#     except Exception as e:
#         dialogs.Messagebox.show_error(f"설정을 저장하는 데 실패했습니다: {e}", title="저장 오류")
#         return False

# def load_settings():
#     default_settings = {"token": "", "username": "", "repo": "", "folder": "", "theme": "litera"}
#     if not os.path.exists(CONFIG_FILE):
#         return default_settings
#     try:
#         with open(CONFIG_FILE, "r", encoding="utf-8") as f:
#             settings = json.load(f)
#             # 이전 버전의 config 파일에 theme이 없을 경우를 대비
#             if "theme" not in settings:
#                 settings["theme"] = "litera"
#             return settings
#     except (json.JSONDecodeError, FileNotFoundError):
#         return default_settings

# # --- API 및 업로드 로직 ---
    
# # --- 백준 문제 불러오기 --- 
# # API 활용했음 

# def fetch_class_problems(class_num):
#     api_url = "https://solved.ac/api/v3/search/problem"
#     params = {"query": f"c:{class_num}", "sort": "level", "direction": "asc"}
#     headers = {"Accept": "application/json"}
#     try:
#         response = requests.get(api_url, params=params, headers=headers)
#         response.raise_for_status()
#         data = response.json()
#         problems = []
#         for item in data.get('items', []):
#             problems.append((str(item['problemId']), item['titleKo']))
#         if not problems:
#             return [], "해당 클래스의 문제 정보를 가져오지 못했습니다."
#         return problems, None
#     except Exception as e:
#         return [], f"API 오류: {e}"


# # --- 파일 업로드 로직 ---

# def upload_file_to_github(local_path, repo_path, settings, log_queue):
#     log_queue.put(f"- 처리 대상: {os.path.basename(local_path)}")
#     url = f"https://api.github.com/repos/{settings['username']}/{settings['repo']}/contents/{repo_path}"
#     headers = {"Authorization": f"token {settings['token']}"}
#     try:
#         with open(local_path, "rb") as file:
#             content_encoded = base64.b64encode(file.read()).decode('utf-8')
#     except (FileNotFoundError, PermissionError) as e:
#         log_queue.put(f"   ❌ 파일 읽기 오류: {e}")
#         return
#     sha = None
#     try:
#         response_get = requests.get(url, headers=headers)
#         if response_get.status_code == 200: sha = response_get.json().get('sha')
#     except: pass
#     data = {"message": f"Auto-upload: {repo_path}", "content": content_encoded}
#     if sha: data["sha"] = sha
#     log_queue.put(f"   🚀 '{repo_path}' 경로로 업로드를 시도합니다...")
#     try:
#         response_put = requests.put(url, headers=headers, data=json.dumps(data))
#         if response_put.status_code in [200, 201]:
#             log_queue.put(f"   ✅ '{os.path.basename(local_path)}' 업로드 성공!")
#         else:
#             log_queue.put(f"   ❌ 업로드 실패! (코드: {response_put.status_code})")
#     except Exception as e:
#         log_queue.put(f"   ❌ 네트워크 오류 (업로드 중): {e}")


# # --- 감시 로직 ---
# class MyEventHandler(FileSystemEventHandler):
#     def __init__(self, settings, log_queue):
#         super().__init__()
#         self.settings = settings
#         self.log_queue = log_queue
#         self.last_processed_time = {}
#     def _should_process(self, path):
#         now = time.time()
#         if now - self.last_processed_time.get(path, 0) < 2: return False
#         self.last_processed_time[path] = now
#         return True
#     def on_created(self, event):
#         if not event.is_directory and self._should_process(event.src_path):
#             time.sleep(1)
#             file_name = os.path.basename(event.src_path)
#             self.log_queue.put(("notification", file_name))
#             repo_file_path = os.path.relpath(event.src_path, self.settings['folder']).replace("\\", "/")
#             upload_file_to_github(event.src_path, repo_file_path, self.settings, self.log_queue)
#     def on_modified(self, event):
#         if not event.is_directory and self._should_process(event.src_path):
#             time.sleep(1)
#             repo_file_path = os.path.relpath(event.src_path, self.settings['folder']).replace("\\", "/")
#             upload_file_to_github(event.src_path, repo_file_path, self.settings, self.log_queue)

# def start_monitoring(settings, log_queue, stop_event):
#     watch_folder = settings['folder']
#     if not os.path.isdir(watch_folder):
#         log_queue.put(f"오류: '{watch_folder}'는 유효한 폴더가 아닙니다. '설정'에서 경로를 확인하세요.")
#         log_queue.put("STOP_MONITORING_UI")
#         return
#     log_queue.put(f"📂 폴더 감시를 시작합니다: {watch_folder}")
#     observer = Observer()
#     observer.schedule(MyEventHandler(settings, log_queue), watch_folder, recursive=True)
#     observer.start()
#     stop_event.wait()
#     observer.stop()
#     observer.join()
#     log_queue.put("⏹️ 감시가 중단되었습니다.")

# # --- UI 로직 --------------------------------------------------------------------------------------------------------------------------------------
# class App:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("자동 업로드 프로그램")
#         self.root.geometry("600x480")

#         self.settings = load_settings()
#         self.log_queue = queue.Queue()
#         self.stop_event = threading.Event()
#         self.problem_window = None

#         # --- 상단 프레임 (설정, 종료 버튼) ---
#         header_frame = ttk.Frame(root, padding=(10, 10, 10, 0))
#         header_frame.pack(fill="x")
#         header_frame.grid_columnconfigure(0, weight=1)
        
#         btn_settings = ttk.Button(header_frame, text="⚙️ 설정", command=self.open_settings_window)
#         btn_settings.grid(row=0, column=1, sticky="e", ipady=8, padx=5)

#         btn_exit = ttk.Button(header_frame, text="🚪 종료", command=self.on_closing, bootstyle="secondary")
#         btn_exit.grid(row=0, column=2, sticky="e", ipady=8)

#         # --- 컨트롤 프레임 (주요 기능 버튼) ---
#         control_frame = ttk.Frame(root, padding=(10, 10))
#         control_frame.pack(fill="x")
#         control_frame.grid_columnconfigure((0, 1, 2), weight=1)

#         self.btn_start = ttk.Button(control_frame, text="감시 시작", command=self.start_action, bootstyle="success")
#         self.btn_start.grid(row=0, column=0, sticky="ew", padx=(0, 5), ipady=10)
        
#         self.btn_stop = ttk.Button(control_frame, text="감시 종료", state="disabled", command=self.stop_action, bootstyle="danger")
#         self.btn_stop.grid(row=0, column=1, sticky="ew", padx=(5, 5), ipady=10)
        
#         self.btn_problem = ttk.Button(control_frame, text="백준 문제 찾기", command=self.open_problem_finder_window, bootstyle="info")
#         self.btn_problem.grid(row=0, column=2, sticky="ew", padx=(5, 0), ipady=10)

#         # --- 로그 프레임 ---
#         log_frame = ttk.Labelframe(root, text="실시간 로그", padding=(10, 5))
#         log_frame.pack(expand=True, fill="both", padx=10, pady=(0, 10))

#         self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state="disabled", font=("Malgun Gothic", 9))
#         self.log_text.pack(expand=True, fill="both")
        
#         self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
#         self.check_log_queue()

#     def open_settings_window(self):
#         settings_win = ttk.Toplevel(self.root)
#         settings_win.title("설정")
#         settings_win.geometry("500x300") # 창 크기 세로로 늘림
#         settings_win.transient(self.root)
#         settings_win.grab_set()

#         frame = ttk.Frame(settings_win, padding=(15, 15))
#         frame.pack(expand=True, fill="both")
#         frame.grid_columnconfigure(1, weight=1)
        
#         # --- 기존 설정 입력 필드 ---
#         fields = ["GitHub 토큰:", "사용자 이름:", "저장소 이름:", "감시할 폴더:"]
#         entries = {}
#         keys = ["token", "username", "repo", "folder"]

#         for i, (label_text, key) in enumerate(zip(fields, keys)):
#             label = ttk.Label(frame, text=label_text)
#             label.grid(row=i, column=0, sticky="w", pady=5)
#             entry = ttk.Entry(frame, show="*" if key == "token" else "")
#             entry.grid(row=i, column=1, columnspan=2, sticky="ew", padx=(10, 0))
#             entry.insert(0, self.settings.get(key, ""))
#             entries[key] = entry
        
#         def select_folder_path():
#             folder_selected = filedialog.askdirectory()
#             if folder_selected:
#                 entries["folder"].delete(0, tk.END)
#                 entries["folder"].insert(0, folder_selected)

#         btn_select = ttk.Button(frame, text="폴더 선택", command=select_folder_path, bootstyle="outline")
#         btn_select.grid(row=3, column=3, padx=(5,0))
        
#         # --- 테마 선택 기능 추가 ---
#         theme_label = ttk.Label(frame, text="테마 선택:")
#         theme_label.grid(row=4, column=0, sticky="w", pady=15)
        
#         theme_names = self.root.style.theme_names() # 사용 가능한 모든 테마 이름 가져오기
#         theme_combo = ttk.Combobox(frame, values=theme_names, state="readonly")
#         theme_combo.grid(row=4, column=1, columnspan=2, sticky="ew", padx=(10, 0))
#         theme_combo.set(self.settings.get("theme", "litera")) # 현재 설정된 테마로 기본값 설정
        
#         # --- 저장 버튼 ---
#         def save_and_close():
#             new_settings = {key: entries[key].get() for key in keys}
#             new_settings["theme"] = theme_combo.get() # 선택된 테마를 설정에 추가
            
#             if save_settings(new_settings):
#                 self.settings = new_settings
#                 dialogs.Messagebox.show_info("설정이 저장되었습니다.\n테마 변경은 프로그램을 재시작해야 적용됩니다.", title="저장 완료", parent=settings_win)
#                 settings_win.destroy()

#         btn_save = ttk.Button(settings_win, text="저장하고 닫기", command=save_and_close, bootstyle="primary")
#         btn_save.pack(pady=(0, 15), ipadx=10)

#     def start_action(self):
#         if not all(self.settings.get(key) for key in ["token", "username", "repo", "folder"]):
#             dialogs.Messagebox.show_error("'⚙️ 설정'에서 모든 정보를 입력해야 합니다.", "오류")
#             return
#         self.log_text.config(state="normal")
#         self.log_text.delete(1.0, tk.END)
#         self.log_text.config(state="disabled")
#         self.btn_start.config(state="disabled")
#         self.btn_stop.config(state="normal")
#         self.stop_event.clear()
#         threading.Thread(target=start_monitoring, args=(self.settings, self.log_queue, self.stop_event), daemon=True).start()

#     def stop_action(self):
#         self.stop_event.set()
#         self.reset_ui_to_idle()
            
#     def reset_ui_to_idle(self):
#         self.btn_start.config(state="normal")
#         self.btn_stop.config(state="disabled")

#     def on_closing(self):
#         if dialogs.Messagebox.show_question("프로그램을 종료하시겠습니까?", "종료 확인") == "Yes":
#             self.stop_event.set()
#             self.root.after(200, self.root.destroy)

#     def check_log_queue(self):
#         while not self.log_queue.empty():
#             message = self.log_queue.get_nowait()
#             if isinstance(message, tuple) and message[0] == "notification":
#                 dialogs.Messagebox.show_info(f"새로운 파일이 생성되었습니다: {message[1]}", "파일 생성 감지")
#                 continue
#             if message == "STOP_MONITORING_UI":
#                 self.reset_ui_to_idle()
#                 continue
#             self.log_text.config(state="normal")
#             self.log_text.insert(tk.END, str(message) + "\n")
#             self.log_text.see(tk.END)
#             self.log_text.config(state="disabled")
#         self.root.after(100, self.check_log_queue)
    
#     def open_problem_finder_window(self):
#         # 이 함수는 이전과 동일
#         if self.problem_window and self.problem_window.winfo_exists():
#             self.problem_window.lift()
#             return
#         self.problem_window = ttk.Toplevel(self.root)
#         self.problem_window.title("solved.ac 문제 찾기")
#         self.problem_window.geometry("500x500")
#         self.problem_window.transient(self.root)
#         class_frame = ttk.Frame(self.problem_window, padding=10)
#         class_frame.pack(fill="x")
#         ttk.Label(class_frame, text="Class 선택 (1-10):").pack(side="left")
#         class_spinbox = ttk.Spinbox(class_frame, from_=1, to=10, width=5)
#         class_spinbox.pack(side="left", padx=5)
#         class_spinbox.set(1)
#         list_frame = ttk.Labelframe(self.problem_window, text="문제 목록", padding=5)
#         list_frame.pack(expand=True, fill="both", padx=10, pady=5)
#         listbox = tk.Listbox(list_frame, font=("Malgun Gothic", 10), relief="flat")
#         listbox.pack(side="left", expand=True, fill="both")
#         scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview, bootstyle="round")
#         scrollbar.pack(side="right", fill="y")
#         listbox.config(yscrollcommand=scrollbar.set)
#         status_label = ttk.Label(self.problem_window, text="클래스를 선택하고 '문제 불러오기'를 누르세요.", anchor="w")
#         status_label.pack(side="bottom", fill="x", padx=10, pady=5)
#         def load_problems_thread():
#             class_num = class_spinbox.get()
#             self.problem_window.after(0, lambda: status_label.config(text=f"Class {class_num} 문제를 불러오는 중..."))
#             self.problem_window.after(0, lambda: listbox.delete(0, tk.END))
#             problems, error = fetch_class_problems(int(class_num))
#             def update_ui():
#                 if error: status_label.config(text=f"오류: {error}"); return
#                 for pid, title in problems: listbox.insert(tk.END, f"{pid} - {title}")
#                 status_label.config(text=f"Class {class_num} 문제 {len(problems)}개 로드 완료. 더블클릭하여 여세요.")
#             self.problem_window.after(0, update_ui)
#         load_button = ttk.Button(class_frame, text="문제 불러오기", command=lambda: threading.Thread(target=load_problems_thread, daemon=True).start(), bootstyle="primary")
#         load_button.pack(side="left", padx=10, ipadx=5)
#         def on_problem_double_click(event):
#             if not listbox.curselection(): return
#             problem_id = listbox.get(listbox.curselection()[0]).split(' - ')[0]
#             webbrowser.open_new_tab(f"https://www.acmicpc.net/problem/{problem_id}")
#             status_label.config(text=f"{problem_id}번 문제를 브라우저에서 엽니다.")
#         listbox.bind("<Double-1>", on_problem_double_click)
# # --- UI 로직 --------------------------------------------------------------------------------------------------------------------------------------

# if __name__ == "__main__":
#     # 프로그램을 시작하기 전, 먼저 설정 파일을 로드합니다.
#     settings = load_settings()
#     # 로드한 설정의 테마로 메인 윈도우를 생성합니다.
#     root = ttk.Window(themename=settings.get("theme", "litera"))
#     app = App(root)
#     root.mainloop()

# env_generator.py - 수정된 최종 버전
import os
import re
import requests
from datetime import datetime

class EnvGenerator:
    def __init__(self):
        self.project_root = os.getcwd()
        self.env_path = os.path.join(self.project_root, '.env')
    
    def validate_token(self, token):
        """GitHub 토큰 실제 검증"""
        if not token:
            return False, "토큰을 입력해주세요."
        
        if not token.startswith(('ghp_', 'github_pat_')):
            return False, "올바른 GitHub 토큰 형식이 아닙니다."
        
        if len(token) < 20:
            return False, "토큰이 너무 짧습니다."
        
        try:
            headers = {"Authorization": f"token {token}"}
            response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                return True, f"토큰이 유효합니다. (사용자: {user_data.get('login', 'Unknown')})"
            elif response.status_code == 401:
                return False, "토큰이 만료되었거나 잘못되었습니다."
            else:
                return False, f"토큰 검증 실패 (상태 코드: {response.status_code})"
        except requests.exceptions.Timeout:
            return False, "토큰 검증 시간 초과. 인터넷 연결을 확인해주세요."
        except requests.exceptions.RequestException:
            return False, "네트워크 오류로 토큰 검증에 실패했습니다."
    
    def validate_username(self, username):
        """GitHub 사용자명 유효성 검사"""
        if not username:
            return False, "사용자명을 입력해주세요."
        
        if not re.match(r'^[a-zA-Z0-9\-]+$', username):
            return False, "사용자명은 영문, 숫자, 하이픈만 사용 가능합니다."
        
        return True, "사용자명이 올바릅니다."
    
    def validate_repo_name(self, repo_name):
        """저장소명 유효성 검사"""
        if not repo_name:
            return False, "저장소명을 입력해주세요."
        
        if not re.match(r'^[a-zA-Z0-9\-_\.]+$', repo_name):
            return False, "저장소명은 영문, 숫자, 하이픈, 언더바, 점만 사용 가능합니다."
        
        return True, "저장소명이 올바릅니다."
    
    def validate_folder_path(self, folder_path):
        """폴더 경로 유효성 검사"""
        if not folder_path:
            return False, "폴더 경로를 입력해주세요."
        
        try:
            normalized_path = os.path.normpath(os.path.expanduser(folder_path))
            
            if os.name == 'nt':  # Windows
                drive, path = os.path.splitdrive(normalized_path)
                if not drive:
                    return False, "Windows에서는 드라이브 문자가 필요합니다 (예: C:\\)"
            
            parent_dir = os.path.dirname(normalized_path)
            if parent_dir and not os.path.exists(parent_dir):
                return False, f"상위 폴더가 존재하지 않습니다: {parent_dir}"
            
            if os.path.exists(normalized_path):
                if not os.access(normalized_path, os.W_OK):
                    return False, "폴더에 쓰기 권한이 없습니다."
            
            return True, "폴더 경로가 올바릅니다."
            
        except Exception as e:
            return False, f"경로 검증 중 오류: {str(e)}"
    
    def validate_repository(self, token, username, repo_name):
        """저장소 존재 및 접근 권한 확인"""
        try:
            headers = {"Authorization": f"token {token}"}
            url = f"https://api.github.com/repos/{username}/{repo_name}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                repo_data = response.json()
                permissions = repo_data.get('permissions', {})
                if permissions.get('push', False):
                    return True, "저장소 접근 및 업로드 권한이 확인되었습니다."
                else:
                    return False, "저장소에 업로드 권한이 없습니다."
            elif response.status_code == 404:
                return False, "저장소를 찾을 수 없습니다."
            elif response.status_code == 403:
                return False, "저장소 접근 권한이 없습니다."
            else:
                return False, f"저장소 확인 실패 (상태 코드: {response.status_code})"
        except:
            return False, "네트워크 오류로 저장소 확인에 실패했습니다."
    
    def validate_time_format(self, hour, minute):
        """시간 형식 유효성 검사"""
        try:
            hour = int(hour)
            minute = int(minute)
            
            if not (0 <= hour <= 23):
                return False, "시간은 0-23 사이여야 합니다."
            
            if not (0 <= minute <= 59):
                return False, "분은 0-59 사이여야 합니다."
            
            return True, f"시간 설정: {hour:02d}:{minute:02d}"
            
        except ValueError:
            return False, "시간과 분은 숫자여야 합니다."
    
    def create_env_file_with_schedule(self, token, username, repo_name, folder_path, 
                                    upload_mode, schedule_hour=None, schedule_minute=None, 
                                    repeat_option="daily"):
        """스케줄링 기능이 포함된 .env 파일 생성"""
        try:
            # 기본 검증
            validations = [
                self.validate_token(token),
                self.validate_username(username),
                self.validate_repo_name(repo_name),
                self.validate_folder_path(folder_path)
            ]
            
            for is_valid, message in validations:
                if not is_valid:
                    return False, message
            
            # 🔧 스케줄 설정 검증 (수정된 부분)
            schedule_config = ""
            if upload_mode in ["schedule", "hybrid"]:
                if schedule_hour is None or schedule_minute is None:
                    return False, "시간 예약 모드에서는 시간을 설정해야 합니다."
                
                time_valid, time_msg = self.validate_time_format(schedule_hour, schedule_minute)
                if not time_valid:
                    return False, time_msg
                
                schedule_config = f"""
# 스케줄 설정
UPLOAD_MODE={upload_mode}
UPLOAD_TIME={schedule_hour:02d}:{schedule_minute:02d}
SCHEDULE_HOUR={schedule_hour}
SCHEDULE_MINUTE={schedule_minute}
REPEAT_OPTION={repeat_option}
"""
            else:
                # 🔧 realtime 모드에서는 기본값 설정
                schedule_config = f"""
# 스케줄 설정
UPLOAD_MODE={upload_mode}
UPLOAD_TIME=00:00
SCHEDULE_HOUR=0
SCHEDULE_MINUTE=0
REPEAT_OPTION={repeat_option}
"""
            
            # 저장소 검증
            repo_valid, repo_message = self.validate_repository(token, username, repo_name)
            if not repo_valid:
                return False, repo_message
            
            # .env 파일 내용 생성
            normalized_path = os.path.normpath(folder_path)
            
            env_content = f"""# GitHub 자동 업로드 설정
# 생성 시간: {self.get_current_time()}

# GitHub 인증 정보
GITHUB_TOKEN={token}
GITHUB_USERNAME={username}
GITHUB_REPO={repo_name}

# 폴더 설정
WATCH_FOLDER={normalized_path}

# 기타 설정
BRANCH=main
COMMIT_MESSAGE_PREFIX=Auto-upload:
{schedule_config}
"""
            
            # 파일 저장
            with open(self.env_path, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            # 감시할 폴더 생성
            if not os.path.exists(normalized_path):
                os.makedirs(normalized_path)
                folder_created = True
            else:
                folder_created = False
            
            # .gitignore 업데이트
            self.update_gitignore()
            
            # 🔧 성공 메시지 생성 (조건부로 수정)
            if upload_mode == "realtime":
                mode_message = "실시간 감시 모드로 설정되었습니다."
            elif upload_mode == "schedule":
                mode_message = f"매일 {schedule_hour:02d}:{schedule_minute:02d}에 업로드됩니다."
            elif upload_mode == "hybrid":
                mode_message = f"실시간 감시 + 매일 {schedule_hour:02d}:{schedule_minute:02d} 업로드로 설정되었습니다."
            else:
                mode_message = "업로드 모드 설정 완료"
            
            success_message = f"""✅ .env 파일 생성 완료!
📁 저장 위치: {self.env_path}
👀 감시 폴더: {normalized_path}
{f"📂 감시 폴더를 새로 생성했습니다." if folder_created else ""}
⏰ {mode_message}
🔒 .gitignore에 .env 추가 완료"""
            
            return True, success_message
            
        except Exception as e:
            return False, f"❌ .env 파일 생성 실패: {str(e)}"
    
    def update_gitignore(self):
        """gitignore 파일 업데이트"""
        gitignore_path = os.path.join(self.project_root, '.gitignore')
        
        gitignore_content = """# Environment Variables
.env
*.env
.env.local
.env.production
.env.development

# Security
token.txt
secrets/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
    
    def get_current_time(self):
        """현재 시간 반환"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def load_existing_env(self):
        """기존 .env 파일이 있으면 내용 로드"""
        if os.path.exists(self.env_path):
            try:
                from dotenv import load_dotenv
                load_dotenv(self.env_path)
                return {
                    'token': os.getenv('GITHUB_TOKEN', ''),
                    'username': os.getenv('GITHUB_USERNAME', ''),
                    'repo_name': os.getenv('GITHUB_REPO', ''),
                    'folder_path': os.getenv('WATCH_FOLDER', '')
                }
            except:
                return None
        return None