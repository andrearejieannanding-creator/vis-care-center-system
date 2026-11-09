import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import os
import json
from datetime import datetime

# Database Configuration
DB_FILE = "care_center.db"

def init_db():
    """Initialize local SQLite database tables with strict indexes for high performance (1,000+ capacity)."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Learners table (Profile Registry)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learners (
            lrn TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            grade TEXT NOT NULL,
            section TEXT NOT NULL,
            gender TEXT NOT NULL,
            guardian TEXT,
            contact TEXT,
            status TEXT DEFAULT 'Active'
        )
    ''')
    
    # 2. Referrals table (Teacher-to-Counselor pipeline)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lrn TEXT NOT NULL,
            referred_by TEXT NOT NULL,
            reason_category TEXT NOT NULL,
            observations TEXT NOT NULL,
            urgency TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            date_submitted TEXT NOT NULL,
            FOREIGN KEY (lrn) REFERENCES learners (lrn)
        )
    ''')
    
    # 3. Anecdotal logs table (Counseling & Interventions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS anecdotal_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lrn TEXT NOT NULL,
            date TEXT NOT NULL,
            incident TEXT NOT NULL,
            action_taken TEXT NOT NULL,
            counselor TEXT NOT NULL,
            FOREIGN KEY (lrn) REFERENCES learners (lrn)
        )
    ''')
    
    # Performance Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_learners_name ON learners(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_referrals_lrn ON referrals(lrn)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_anecdotal_lrn ON anecdotal_logs(lrn)")
    
    conn.commit()
    conn.close()

init_db()

class CareCenterApp(tk.Tk):
    """Main Desktop Application Window for Victoria Integrated School - CARE Center System."""
    
    def __init__(self):
        super().__init__()
        self.title("Victoria Integrated School - CARE Center Learner System")
        self.geometry("1180x740")
        self.minsize(980, 640)
        self.configure(bg="#F8FAFC")
        
        self.passcode = "1234"
        self.authenticated = False
        
        # Configure TTK Theme and Styles
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        # Color Palette
        self.PRIMARY_COLOR = "#065F46"     # Emerald Dark
        self.ACCENT_COLOR = "#059669"      # Emerald Medium
        self.WARNING_COLOR = "#D97706"     # Amber
        self.TEXT_COLOR = "#1E293B"        # Slate Dark
        
        self.configure_styles()
        self.create_lock_screen()

    def configure_styles(self):
        """Define custom UI styles for widgets."""
        self.style.configure("TFrame", background="#F8FAFC")
        self.style.configure("Header.TFrame", background=self.PRIMARY_COLOR)
        self.style.configure("Header.TLabel", background=self.PRIMARY_COLOR, foreground="white", font=("Segoe UI", 13, "bold"))
        self.style.configure("SubHeader.TLabel", background=self.PRIMARY_COLOR, foreground="#A7F3D0", font=("Segoe UI", 9))
        self.style.configure("TNotebook", background="#F8FAFC", borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 9, "bold"), padding=[14, 7], background="#E2E8F0")
        self.style.map("TNotebook.Tab", background=[("selected", self.PRIMARY_COLOR)], foreground=[("selected", "white")])
        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#E2E8F0", foreground="#334155")
        self.style.configure("Treeview", font=("Segoe UI", 9), rowheight=26)

    # ------------------- LOCK SCREEN (PASSCODE GATE) -------------------
    def create_lock_screen(self):
        """Display passcode barrier for R.A. 10173 compliance."""
        self.lock_frame = tk.Frame(self, bg=self.PRIMARY_COLOR)
        self.lock_frame.pack(fill="both", expand=True)

        box = tk.Frame(self.lock_frame, bg="white", padx=45, pady=40, relief="flat", highlightbackground="#CBD5E1", highlightthickness=1)
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(box, text="🔒 CARE Center Security Gate", font=("Segoe UI", 16, "bold"), bg="white", fg=self.PRIMARY_COLOR).pack(pady=(0, 4))
        tk.Label(box, text="Republic Act 10173 (Data Privacy Act) Compliant", font=("Segoe UI", 9), bg="white", fg="#64748B").pack(pady=(0, 20))

        tk.Label(box, text="Enter Access Passcode:", font=("Segoe UI", 9, "bold"), bg="white", fg=self.TEXT_COLOR).pack(anchor="w")
        self.pass_entry = tk.Entry(box, show="•", font=("Segoe UI", 14), justify="center", bd=1, relief="solid")
        self.pass_entry.pack(fill="x", pady=(4, 15))
        self.pass_entry.focus()
        self.pass_entry.bind("<Return>", lambda e: self.unlock())

        btn = tk.Button(box, text="Unlock CARE Portal", font=("Segoe UI", 10, "bold"), bg=self.ACCENT_COLOR, fg="white", activebackground="#047857", activeforeground="white", bd=0, pady=8, cursor="hand2", command=self.unlock)
        btn.pack(fill="x")
        
        tk.Label(box, text="Default Passcode: 1234", font=("Segoe UI", 8), bg="white", fg="#94A3B8").pack(pady=(15, 0))

    def unlock(self):
        """Authenticate user against set passcode."""
        if self.pass_entry.get() == self.passcode:
            self.authenticated = True
            self.lock_frame.destroy()
            self.build_main_ui()
        else:
            messagebox.showerror("Access Denied", "Incorrect Passcode. Please try again.")
            self.pass_entry.delete(0, tk.END)

    # ------------------- MAIN INTERFACE BUILDER -------------------
    def build_main_ui(self):
        """Construct top header, navigation tabs, and system layout."""
        header = ttk.Frame(self, style="Header.TFrame", padding=14)
        header.pack(fill="x")
        
        title_box = tk.Frame(header, bg=self.PRIMARY_COLOR)
        title_box.pack(side="left")
        
        ttk.Label(title_box, text="Victoria Integrated School — CARE Center", style="Header.TLabel").pack(anchor="w")
        ttk.Label(title_box, text="Learner Profiling & Referral Management System (1,000 Capacity)", style="SubHeader.TLabel").pack(anchor="w")

        right_btns = tk.Frame(header, bg=self.PRIMARY_COLOR)
        right_btns.pack(side="right")

        tk.Button(right_btns, text="⚙️ Settings", bg="#047857", fg="white", font=("Segoe UI", 9, "bold"), bd=0, padx=10, pady=5, cursor="hand2", command=self.open_settings).pack(side="left", padx=5)
        tk.Button(right_btns, text="🔒 Lock System", bg="#DC2626", fg="white", font=("Segoe UI", 9, "bold"), bd=0, padx=10, pady=5, cursor="hand2", command=self.relock).pack(side="left")

        # Main Navigation Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=14)

        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_learners = ttk.Frame(self.notebook)
        self.tab_referrals = ttk.Frame(self.notebook)
        self.tab_anecdotal = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_dashboard, text=" Dashboard ")
        self.notebook.add(self.tab_learners, text=" Learner Directory ")
        self.notebook.add(self.tab_referrals, text=" Submit & View Referrals ")
        self.notebook.add(self.tab_anecdotal, text=" Anecdotal Records ")

        self.build_dashboard()
        self.build_learners_tab()
        self.build_referrals_tab()
        self.build_anecdotal_tab()

    def relock(self):
        """Lock current session and show passcode screen."""
        self.notebook.destroy()
        self.create_lock_screen()

    # ------------------- DASHBOARD TAB -------------------
    def build_dashboard(self):
        container = tk.Frame(self.tab_dashboard, bg="#F8FAFC", padx=20, pady=20)
        container.pack(fill="both", expand=True)

        cards_frame = tk.Frame(container, bg="#F8FAFC")
        cards_frame.pack(fill="x", pady=(0, 20))

        self.stat_learners = self.create_card(cards_frame, "Total Enrolled Learners", "0", "#0284C7")
        self.stat_referrals = self.create_card(cards_frame, "Active Referrals", "0", "#D97706")
        self.stat_anecdotal = self.create_card(cards_frame, "Anecdotal Records", "0", "#059669")

        # Quick Control Panel
        actions_box = tk.LabelFrame(container, text=" Quick Management Actions ", font=("Segoe UI", 10, "bold"), bg="white", fg=self.TEXT_COLOR, padx=15, pady=15)
        actions_box.pack(fill="x", pady=10)

        tk.Button(actions_box, text="+ Add Single Learner", bg="#0284C7", fg="white", font=("Segoe UI", 9, "bold"), padx=12, pady=6, bd=0, cursor="hand2", command=self.popup_add_learner).pack(side="left", padx=5)
        tk.Button(actions_box, text="📁 Batch Import SF1 (CSV)", bg="#0D9488", fg="white", font=("Segoe UI", 9, "bold"), padx=12, pady=6, bd=0, cursor="hand2", command=self.import_csv).pack(side="left", padx=5)
        tk.Button(actions_box, text="⚠️ Submit Teacher Referral", bg="#D97706", fg="white", font=("Segoe UI", 9, "bold"), padx=12, pady=6, bd=0, cursor="hand2", command=lambda: self.notebook.select(2)).pack(side="left", padx=5)

        self.refresh_stats()

    def create_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg="white", padx=20, pady=16, highlightbackground="#E2E8F0", highlightthickness=1)
        card.pack(side="left", expand=True, fill="x", padx=5)

        tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), bg="white", fg="#64748B").pack(anchor="w")
        lbl_val = tk.Label(card, text=value, font=("Segoe UI", 22, "bold"), bg="white", fg=color)
        lbl_val.pack(anchor="w")
        return lbl_val

    def refresh_stats(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM learners")
        self.stat_learners.config(text=str(cursor.fetchone()[0]))

        cursor.execute("SELECT COUNT(*) FROM referrals WHERE status != 'Resolved'")
        self.stat_referrals.config(text=str(cursor.fetchone()[0]))

        cursor.execute("SELECT COUNT(*) FROM anecdotal_logs")
        self.stat_anecdotal.config(text=str(cursor.fetchone()[0]))

        conn.close()

    # ------------------- LEARNER DIRECTORY TAB -------------------
    def build_learners_tab(self):
        frame = tk.Frame(self.tab_learners, bg="#F8FAFC", padx=15, pady=15)
        frame.pack(fill="both", expand=True)

        top_bar = tk.Frame(frame, bg="#F8FAFC")
        top_bar.pack(fill="x", pady=(0, 10))

        tk.Label(top_bar, text="Search Learner:", font=("Segoe UI", 9, "bold"), bg="#F8FAFC").pack(side="left", padx=(0, 5))
        self.search_entry = tk.Entry(top_bar, font=("Segoe UI", 10), width=32)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_learners())

        tk.Button(top_bar, text="+ Add Learner Profile", bg=self.ACCENT_COLOR, fg="white", font=("Segoe UI", 9, "bold"), bd=0, padx=12, pady=5, cursor="hand2", command=self.popup_add_learner).pack(side="right")

        columns = ("lrn", "name", "grade", "section", "gender", "guardian", "contact")
        self.learner_tree = ttk.Treeview(frame, columns=columns, show="headings")

        self.learner_tree.heading("lrn", text="LRN")
        self.learner_tree.heading("name", text="Full Name")
        self.learner_tree.heading("grade", text="Grade Level")
        self.learner_tree.heading("section", text="Section")
        self.learner_tree.heading("gender", text="Gender")
        self.learner_tree.heading("guardian", text="Guardian")
        self.learner_tree.heading("contact", text="Contact No.")

        self.learner_tree.column("lrn", width=120)
        self.learner_tree.column("name", width=220)
        self.learner_tree.column("grade", width=90)
        self.learner_tree.column("section", width=100)
        self.learner_tree.column("gender", width=80)
        self.learner_tree.column("guardian", width=180)
        self.learner_tree.column("contact", width=120)

        self.learner_tree.pack(fill="both", expand=True)
        self.load_learners()

    def load_learners(self):
        for item in self.learner_tree.get_children():
            self.learner_tree.delete(item)

        query = self.search_entry.get().strip()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        if query:
            cursor.execute("SELECT lrn, name, grade, section, gender, guardian, contact FROM learners WHERE name LIKE ? OR lrn LIKE ? ORDER BY name ASC", (f"%{query}%", f"%{query}%"))
        else:
            cursor.execute("SELECT lrn, name, grade, section, gender, guardian, contact FROM learners ORDER BY name ASC")

        for row in cursor.fetchall():
            self.learner_tree.insert("", "end", values=row)

        conn.close()

    def popup_add_learner(self):
        win = tk.Toplevel(self)
        win.title("Add New Learner Profile")
        win.geometry("420x500")
        win.configure(bg="white", padx=20, pady=20)

        fields = [("LRN (12 Digits):", "lrn"), ("Full Name (Last, First MI):", "name"), 
                  ("Grade Level (K-7):", "grade"), ("Section:", "section"), 
                  ("Gender (Male/Female):", "gender"), ("Parent/Guardian Name:", "guardian"), 
                  ("Contact Number:", "contact")]
        entries = {}

        for label, key in fields:
            tk.Label(win, text=label, font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w", pady=(4, 0))
            ent = tk.Entry(win, font=("Segoe UI", 10), bd=1, relief="solid")
            ent.pack(fill="x", pady=(0, 4))
            entries[key] = ent

        def save():
            lrn = entries["lrn"].get().strip()
            name = entries["name"].get().strip()
            grade = entries["grade"].get().strip()
            section = entries["section"].get().strip()
            gender = entries["gender"].get().strip()
            guardian = entries["guardian"].get().strip()
            contact = entries["contact"].get().strip()

            if not lrn or not name or not grade or not section:
                messagebox.showerror("Required Fields", "Please complete LRN, Name, Grade, and Section.")
                return

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO learners VALUES (?, ?, ?, ?, ?, ?, ?, 'Active')", 
                               (lrn, name, grade, section, gender, guardian, contact))
                conn.commit()
                messagebox.showinfo("Success", "Learner profile added successfully!")
                win.destroy()
                self.load_learners()
                self.refresh_stats()
            except sqlite3.IntegrityError:
                messagebox.showerror("Duplicate Record", "A learner with this LRN already exists.")
            finally:
                conn.close()

        tk.Button(win, text="Save Profile", bg=self.ACCENT_COLOR, fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=8, cursor="hand2", command=save).pack(fill="x", pady=(15, 0))

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        added, skipped = 0, 0

        try:
            with open(file_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        cursor.execute("INSERT INTO learners VALUES (?, ?, ?, ?, ?, ?, ?, 'Active')",
                                       (row['lrn'], row['name'], row['grade'], row['section'], row.get('gender', ''), row.get('guardian', ''), row.get('contact', '')))
                        added += 1
                    except sqlite3.IntegrityError:
                        skipped += 1
            conn.commit()
            messagebox.showinfo("Import Complete", f"Import Summary:\n- Successfully Added: {added}\n- Skipped Duplicates: {skipped}")
            self.load_learners()
            self.refresh_stats()
        except Exception as e:
            messagebox.showerror("CSV Format Error", f"Failed to parse CSV file.\nEnsure headers are: lrn, name, grade, section, gender, guardian, contact\n\nError details: {str(e)}")
        finally:
            conn.close()

    # ------------------- REFERRALS TAB -------------------
    def build_referrals_tab(self):
        frame = tk.Frame(self.tab_referrals, bg="#F8FAFC", padx=15, pady=15)
        frame.pack(fill="both", expand=True)

        left = tk.LabelFrame(frame, text=" Submit Student Referral ", font=("Segoe UI", 10, "bold"), bg="white", padx=15, pady=15)
        left.pack(side="left", fill="y", padx=(0, 10))

        tk.Label(left, text="Learner LRN / Name:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w")
        self.ref_lrn_entry = tk.Entry(left, font=("Segoe UI", 10), bd=1, relief="solid")
        self.ref_lrn_entry.pack(fill="x", pady=(2, 8))

        tk.Label(left, text="Referring Teacher / Adviser:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w")
        self.ref_by_entry = tk.Entry(left, font=("Segoe UI", 10), bd=1, relief="solid")
        self.ref_by_entry.pack(fill="x", pady=(2, 8))

        tk.Label(left, text="Reason Category:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w")
        self.ref_cat_cb = ttk.Combobox(left, values=["Behavioral / Discipline", "Emotional / Mental Health", "Academic Drop", "Frequent Absenteeism", "Bullying Incident", "Family Concern"], state="readonly")
        self.ref_cat_cb.pack(fill="x", pady=(2, 8))
        self.ref_cat_cb.current(0)

        tk.Label(left, text="Urgency Level:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w")
        self.ref_urg_cb = ttk.Combobox(left, values=["Normal", "Urgent", "Emergency / Critical"], state="readonly")
        self.ref_urg_cb.pack(fill="x", pady=(2, 8))
        self.ref_urg_cb.current(0)

        tk.Label(left, text="Detailed Observations:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w")
        self.ref_obs_text = tk.Text(left, height=5, font=("Segoe UI", 9), bd=1, relief="solid")
        self.ref_obs_text.pack(fill="x", pady=(2, 10))

        tk.Button(left, text="Submit Referral to CARE Center", bg=self.WARNING_COLOR, fg="white", font=("Segoe UI", 9, "bold"), bd=0, pady=8, cursor="hand2", command=self.save_referral).pack(fill="x")

        right = tk.Frame(frame, bg="#F8FAFC")
        right.pack(side="right", fill="both", expand=True)

        columns = ("id", "lrn", "referred_by", "category", "urgency", "date", "status")
        self.ref_tree = ttk.Treeview(right, columns=columns, show="headings")
        self.ref_tree.heading("id", text="Ref ID")
        self.ref_tree.heading("lrn", text="Learner LRN")
        self.ref_tree.heading("referred_by", text="Referred By")
        self.ref_tree.heading("category", text="Category")
        self.ref_tree.heading("urgency", text="Urgency")
        self.ref_tree.heading("date", text="Date")
        self.ref_tree.heading("status", text="Status")

        self.ref_tree.column("id", width=55)
        self.ref_tree.column("lrn", width=110)
        self.ref_tree.column("referred_by", width=120)
        self.ref_tree.column("category", width=140)
        self.ref_tree.column("urgency", width=90)
        self.ref_tree.column("date", width=90)
        self.ref_tree.column("status", width=80)

        self.ref_tree.pack(fill="both", expand=True)
        self.load_referrals()

    def save_referral(self):
        lrn = self.ref_lrn_entry.get().strip()
        ref_by = self.ref_by_entry.get().strip()
        cat = self.ref_cat_cb.get()
        urg = self.ref_urg_cb.get()
        obs = self.ref_obs_text.get("1.0", tk.END).strip()
        date_str = datetime.now().strftime("%Y-%m-%d")

        if not lrn or not ref_by or not obs:
            messagebox.showerror("Error", "Please complete all referral fields.")
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO referrals (lrn, referred_by, reason_category, observations, urgency, status, date_submitted) VALUES (?, ?, ?, ?, ?, 'Pending', ?)",
                       (lrn, ref_by, cat, obs, urg, date_str))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Referral recorded and forwarded to CARE Center!")
        self.ref_lrn_entry.delete(0, tk.END)
        self.ref_by_entry.delete(0, tk.END)
        self.ref_obs_text.delete("1.0", tk.END)
        self.load_referrals()
        self.refresh_stats()

    def load_referrals(self):
        for item in self.ref_tree.get_children():
            self.ref_tree.delete(item)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, lrn, referred_by, reason_category, urgency, date_submitted, status FROM referrals ORDER BY id DESC")
        for row in cursor.fetchall():
            self.ref_tree.insert("", "end", values=row)
        conn.close()

    # ------------------- ANECDOTAL RECORDS TAB -------------------
    def build_anecdotal_tab(self):
        frame = tk.Frame(self.tab_anecdotal, bg="#F8FAFC", padx=15, pady=15)
        frame.pack(fill="both", expand=True)

        top_bar = tk.Frame(frame, bg="#F8FAFC")
        top_bar.pack(fill="x", pady=(0, 10))

        tk.Button(top_bar, text="+ Log Anecdotal / Counseling Session Note", bg=self.ACCENT_COLOR, fg="white", font=("Segoe UI", 9, "bold"), bd=0, padx=12, pady=5, cursor="hand2", command=self.popup_add_anecdotal).pack(side="left")

        columns = ("id", "lrn", "date", "incident", "action", "counselor")
        self.anec_tree = ttk.Treeview(frame, columns=columns, show="headings")
        self.anec_tree.heading("id", text="Log ID")
        self.anec_tree.heading("lrn", text="Learner LRN")
        self.anec_tree.heading("date", text="Date")
        self.anec_tree.heading("incident", text="Observed Incident / Conversation")
        self.anec_tree.heading("action", text="Action Taken / Counseling Plan")
        self.anec_tree.heading("counselor", text="Counselor / Designate")

        self.anec_tree.column("id", width=60)
        self.anec_tree.column("lrn", width=110)
        self.anec_tree.column("date", width=90)
        self.anec_tree.column("incident", width=260)
        self.anec_tree.column("action", width=260)
        self.anec_tree.column("counselor", width=140)

        self.anec_tree.pack(fill="both", expand=True)
        self.load_anecdotal()

    def load_anecdotal(self):
        for item in self.anec_tree.get_children():
            self.anec_tree.delete(item)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, lrn, date, incident, action_taken, counselor FROM anecdotal_logs ORDER BY id DESC")
        for row in cursor.fetchall():
            self.anec_tree.insert("", "end", values=row)
        conn.close()

    def popup_add_anecdotal(self):
        win = tk.Toplevel(self)
        win.title("Log Anecdotal Session Note")
        win.geometry("460x440")
        win.configure(bg="white", padx=20, pady=20)

        tk.Label(win, text="Learner LRN:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w")
        lrn_ent = tk.Entry(win, font=("Segoe UI", 10), bd=1, relief="solid")
        lrn_ent.pack(fill="x", pady=(0, 8))

        tk.Label(win, text="Counselor / Designate Name:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w")
        coun_ent = tk.Entry(win, font=("Segoe UI", 10), bd=1, relief="solid")
        coun_ent.pack(fill="x", pady=(0, 8))

        tk.Label(win, text="Observed Incident / Session Notes:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w")
        inc_txt = tk.Text(win, height=4, font=("Segoe UI", 9), bd=1, relief="solid")
        inc_txt.pack(fill="x", pady=(0, 8))

        tk.Label(win, text="Action Taken / Intervention Plan:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w")
        act_txt = tk.Text(win, height=4, font=("Segoe UI", 9), bd=1, relief="solid")
        act_txt.pack(fill="x", pady=(0, 10))

        def save():
            lrn = lrn_ent.get().strip()
            coun = coun_ent.get().strip()
            inc = inc_txt.get("1.0", tk.END).strip()
            act = act_txt.get("1.0", tk.END).strip()
            date_str = datetime.now().strftime("%Y-%m-%d")

            if not lrn or not coun or not inc or not act:
                messagebox.showerror("Required Fields", "Please complete all fields.")
                return

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO anecdotal_logs (lrn, date, incident, action_taken, counselor) VALUES (?, ?, ?, ?, ?)",
                           (lrn, date_str, inc, act, coun))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Anecdotal record successfully saved!")
            win.destroy()
            self.load_anecdotal()
            self.refresh_stats()

        tk.Button(win, text="Save Anecdotal Record", bg=self.ACCENT_COLOR, fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=8, cursor="hand2", command=save).pack(fill="x")

    # ------------------- SETTINGS & PASSCODE MODAL -------------------
    def open_settings(self):
        win = tk.Toplevel(self)
        win.title("CARE Center Settings & Security Configuration")
        win.geometry("420x420")
        win.configure(bg="white", padx=20, pady=20)

        tk.Label(win, text="⚙️ Security & Passcode Configuration", font=("Segoe UI", 11, "bold"), bg="white", fg=self.PRIMARY_COLOR).pack(anchor="w", pady=(0, 10))

        tk.Label(win, text="New Access Passcode:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w")
        new_pass_entry = tk.Entry(win, show="•", font=("Segoe UI", 11), bd=1, relief="solid")
        new_pass_entry.pack(fill="x", pady=(2, 10))

        def update_passcode():
            val = new_pass_entry.get().strip()
            if len(val) < 4:
                messagebox.showerror("Error", "Passcode must be at least 4 characters long.")
                return
            self.passcode = val
            messagebox.showinfo("Success", "Security passcode updated successfully!")
            win.destroy()

        tk.Button(win, text="Update Passcode", bg=self.ACCENT_COLOR, fg="white", font=("Segoe UI", 9, "bold"), bd=0, pady=6, cursor="hand2", command=update_passcode).pack(fill="x", pady=(0, 15))

        # Seed Sample Test Data Button
        def seed_sample_data():
            if messagebox.askyesno("Load Test Data", "Do you want to insert 5 sample student records and referrals for testing?"):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                sample_learners = [
                    ('109823456701', 'Dela Cruz, Juan', '7', 'Rizal', 'Male', 'Maria Dela Cruz', '09171234567'),
                    ('109823456702', 'Santos, Maria', '7', 'Rizal', 'Female', 'Jose Santos', '09187654321'),
                    ('109823456703', 'Reyes, Pedro', '6', ' Bonifacio', 'Male', 'Ana Reyes', '09198887766'),
                    ('109823456704', 'Gonzales, Angela', '5', 'Mabini', 'Female', 'Elena Gonzales', '09201112233'),
                    ('109823456705', 'Torres, Mark', '4', 'Luna', 'Male', 'Roberto Torres', '09223334455')
                ]
                for record in sample_learners:
                    try:
                        cursor.execute("INSERT INTO learners VALUES (?, ?, ?, ?, ?, ?, ?, 'Active')", record)
                    except sqlite3.IntegrityError:
                        pass
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Sample records loaded!")
                win.destroy()
                self.load_learners()
                self.refresh_stats()

        tk.Button(win, text="🌱 Load 5 Sample Test Profiles", bg="#0284C7", fg="white", font=("Segoe UI", 9, "bold"), bd=0, pady=6, cursor="hand2", command=seed_sample_data).pack(fill="x", pady=(0, 15))

        tk.Label(win, text="⚠️ Danger Zone", font=("Segoe UI", 10, "bold"), bg="white", fg="#DC2626").pack(anchor="w", pady=(5, 5))

        def clear_all():
            if messagebox.askyesno("Confirm Data Reset", "Are you sure you want to delete ALL student profiles, referrals, and logs? This action cannot be undone."):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM learners")
                cursor.execute("DELETE FROM referrals")
                cursor.execute("DELETE FROM anecdotal_logs")
                conn.commit()
                conn.close()
                messagebox.showinfo("Reset Complete", "All database records cleared.")
                win.destroy()
                self.load_learners()
                self.load_referrals()
                self.load_anecdotal()
                self.refresh_stats()

        tk.Button(win, text="Clear All Database Records", bg="#DC2626", fg="white", font=("Segoe UI", 9, "bold"), bd=0, pady=6, cursor="hand2", command=clear_all).pack(fill="x")

if __name__ == "__main__":
    app = CareCenterApp()
    app.mainloop()
