from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarIconListItem, ImageLeftWidget, IconRightWidget
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from datetime import datetime
import os
import database

# Export Libraries
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Simulate a mobile screen size on your computer
Window.size = (360, 640)

KV = '''
MDScreen:
    
    MDBoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            title: "ABS Mallakhamb Academy"
            elevation: 4
            right_action_items: [["theme-light-dark", lambda x: app.toggle_theme()]]

        MDBottomNavigation:
            panel_color: app.theme_cls.bg_dark
            
            # STUDENTS TAB
            MDBottomNavigationItem:
                name: 'screen 1'
                text: 'Students'
                icon: 'account-group'
                on_tab_press: app.load_students()

                MDBoxLayout:
                    orientation: "vertical"
                    
                    MDScrollView:
                        MDList:
                            id: student_list

                MDFloatingActionButton:
                    icon: "plus"
                    pos_hint: {"center_x": .85, "center_y": .1}
                    on_release: app.show_add_student_dialog()

            # ATTENDANCE TAB
            MDBottomNavigationItem:
                name: 'screen 2'
                text: 'Attendance'
                icon: 'calendar-check'
                on_tab_press: app.load_attendance_list()

                MDBoxLayout:
                    orientation: "vertical"
                    padding: "10dp"
                    spacing: "10dp"
                    
                    MDLabel:
                        id: attendance_date_label
                        text: "Today's Attendance"
                        halign: "center"
                        font_style: "H6"
                        size_hint_y: None
                        height: "40dp"
                    
                    MDScrollView:
                        MDList:
                            id: attendance_list

            # EXPORTS TAB
            MDBottomNavigationItem:
                name: 'screen 3'
                text: 'Reports'
                icon: 'file-chart'

                MDBoxLayout:
                    orientation: "vertical"
                    spacing: "24dp"
                    padding: "24dp"
                    adaptive_height: True
                    pos_hint: {"center_x": .5, "center_y": .5}
                    
                    MDLabel:
                        text: "Management Reports"
                        halign: "center"
                        font_style: "H5"
                        bold: True
                    
                    MDRaisedButton:
                        text: "Export Attendance to Excel"
                        icon: "file-excel"
                        pos_hint: {"center_x": .5}
                        size_hint_x: 0.8
                        on_release: app.export_attendance_excel()
                        
                    MDRaisedButton:
                        text: "Export Roster + Attendance to PDF"
                        icon: "file-pdf-box"
                        pos_hint: {"center_x": .5}
                        size_hint_x: 0.8
                        on_release: app.export_student_pdf()
'''

class AcademyApp(MDApp):
    dialog = None
    selected_photo_path = ""

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepOrange"
        
        # Initialize Database
        database.create_tables()
        self.apply_database_migrations()
        
        return Builder.load_string(KV)

    def on_start(self):
        self.load_students()
        today_str = datetime.now().strftime("%B %d, %Y")
        self.root.ids.attendance_date_label.text = f"Attendance: {today_str}"

    def toggle_theme(self):
        self.theme_cls.theme_style = (
            "Light" if self.theme_cls.theme_style == "Dark" else "Dark"
        )

    def apply_database_migrations(self):
        """Safely updates old database versions to include the photo tracking column."""
        conn = database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN photo TEXT DEFAULT ''")
            conn.commit()
        except Exception:
            # Column already exists, safe to ignore
            pass
        finally:
            conn.close()

    # ==========================
    # STUDENT MANAGEMENT METHODS
    # ==========================
    def load_students(self, *args):
        self.root.ids.student_list.clear_widgets()
        
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, phone, photo FROM students")
        students = cursor.fetchall()
        conn.close()
        
        for student in students:
            student_id, name, phone, photo_path = student
            item = TwoLineAvatarIconListItem(
                text=name,
                secondary_text=f"Phone: {phone}"
            )
            
            # Set custom image if valid; fall back to logo placeholder
            img_src = photo_path if photo_path and os.path.exists(photo_path) else "assets/logo.png"
            avatar = ImageLeftWidget(source=img_src)
            item.add_widget(avatar)
            self.root.ids.student_list.add_widget(item)

    def show_add_student_dialog(self):
        self.selected_photo_path = "" # Reset selection
        
        self.name_field = MDTextField(hint_text="Student Name")
        self.phone_field = MDTextField(hint_text="Phone Number")
        
        dialog_layout = MDBoxLayout(orientation="vertical", spacing="12dp", size_hint_y=None, height="180dp")
        dialog_layout.add_widget(self.name_field)
        dialog_layout.add_widget(self.phone_field)
        
        # Image Picker Sub-Layout
        picker_layout = MDBoxLayout(orientation="horizontal", spacing="10dp", size_hint_y=None, height="40dp")
        self.photo_btn = MDRaisedButton(text="Select Photo", on_release=self.open_file_chooser)
        self.photo_label = MDLabel(text="No file chosen", halign="left", valign="middle")
        
        picker_layout.add_widget(self.photo_btn)
        picker_layout.add_widget(self.photo_label)
        dialog_layout.add_widget(picker_layout)

        self.dialog = MDDialog(
            title="Add New Student",
            type="custom",
            content_cls=dialog_layout,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="SAVE", on_release=self.save_student),
            ],
        )
        self.dialog.open()

    def open_file_chooser(self, *args):
        """Launches a file browser window filtered to image formats."""
        file_chooser = FileChooserIconView(filters=['*.png', '*.jpg', '*.jpeg'])
        
        popup_layout = MDBoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        popup_layout.add_widget(file_chooser)
        
        select_btn = MDRaisedButton(text="Confirm Image Selection", pos_hint={"center_x": .5})
        popup_layout.add_widget(select_btn)
        
        file_popup = Popup(title="Browse System Images", content=popup_layout, size_hint=(0.9, 0.9))
        
        def confirm_selection(*args):
            if file_chooser.selection:
                self.selected_photo_path = file_chooser.selection[0]
                self.photo_label.text = os.path.basename(self.selected_photo_path)
            file_popup.dismiss()
            
        select_btn.bind(on_release=confirm_selection)
        file_popup.open()

    def save_student(self, *args):
        name = self.name_field.text
        phone = self.phone_field.text
        photo = self.selected_photo_path
        
        if name:
            conn = database.connect()
            cursor = conn.cursor()
            today_date = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("INSERT INTO students (name, phone, join_date, photo) VALUES (?, ?, ?, ?)", 
                           (name, phone, today_date, photo))
            conn.commit()
            conn.close()
            
            self.dialog.dismiss()
            self.load_students()

    # ==========================
    # ATTENDANCE TRACKING METHODS
    # ==========================
    def load_attendance_list(self, *args):
        self.root.ids.attendance_list.clear_widgets()
        today = datetime.now().strftime("%Y-%m-%d")
        
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, photo FROM students")
        students = cursor.fetchall()
        
        for student in students:
            student_id, name, photo_path = student
            
            cursor.execute("SELECT status FROM attendance WHERE student_id = ? AND date = ?", (student_id, today))
            row = cursor.fetchone()
            status = row[0] if row else "Absent"
            
            item = TwoLineAvatarIconListItem(
                text=name,
                secondary_text=f"Today's Status: {status}"
            )
            
            img_src = photo_path if photo_path and os.path.exists(photo_path) else "assets/logo.png"
            avatar = ImageLeftWidget(source=img_src)
            item.add_widget(avatar)
            
            icon_name = "check-circle" if status == "Present" else "checkbox-blank-circle-outline"
            icon_widget = IconRightWidget(icon=icon_name)
            icon_widget.bind(on_release=lambda x, sid=student_id, sstat=status: self.toggle_attendance(sid, sstat))
            item.add_widget(icon_widget)
            
            self.root.ids.attendance_list.add_widget(item)
            
        conn.close()

    def toggle_attendance(self, student_id, current_status):
        today = datetime.now().strftime("%Y-%m-%d")
        new_status = "Present" if current_status == "Absent" else "Absent"
        
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM attendance WHERE student_id = ? AND date = ?", (student_id, today))
        row = cursor.fetchone()
        
        if row:
            cursor.execute("UPDATE attendance SET status = ? WHERE student_id = ? AND date = ?", (new_status, student_id, today))
        else:
            cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)", (student_id, today, new_status))
            
        conn.commit()
        conn.close()
        self.load_attendance_list()

    # ==========================
    # REPORT GENERATION METHODS
    # ==========================
    def export_attendance_excel(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Attendance Logs"
        ws.append(["Record ID", "Student Name", "Date Label", "Status"])
        
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, s.name, a.date, a.status 
            FROM attendance a 
            JOIN students s ON a.student_id = s.id
            ORDER BY a.date DESC
        """)
        for row in cursor.fetchall():
            ws.append(row)
        conn.close()
        
        filename = "Attendance_Report.xlsx"
        wb.save(filename)
        self.show_alert_dialog("Success", f"Excel report successfully saved as:\n📁 {filename}")

    def export_student_pdf(self):
        filename = "Academy_Roster_Attendance.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Header Document Block
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, 750, "Mallakhamb Academy")
        c.setFont("Helvetica", 12)
        c.drawString(50, 730, f"Comprehensive Roster & Attendance Status — Run Date: {today}")
        c.line(50, 715, 550, 715)
        
        # Table Headers Setup
        c.setFont("Helvetica-Bold", 11)
        c.drawString(60, 690, "ID")
        c.drawString(100, 690, "Student Full Name")
        c.drawString(280, 690, "Primary Contact")
        c.drawString(430, 690, "Today's Status")
        c.line(50, 680, 550, 680)
        
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, s.name, s.phone, COALESCE(a.status, 'Absent') 
            FROM students s 
            LEFT JOIN attendance a ON s.id = a.student_id AND a.date = ?
        """, (today,))
        dataset = cursor.fetchall()
        conn.close()
        
        y_position = 650
        c.setFont("Helvetica", 10)
        
        for record in dataset:
            student_id, name, phone, status = record
            c.drawString(60, y_position, str(student_id))
            c.drawString(100, y_position, name)
            c.drawString(280, y_position, str(phone))
            
            if status == "Present":
                c.setFont("Helvetica-Bold", 10)
            c.drawString(430, y_position, status)
            c.setFont("Helvetica", 10)
            
            y_position -= 25
            
            if y_position < 50:
                c.showPage()
                y_position = 750
                c.setFont("Helvetica", 10)
                
        c.save()
        self.show_alert_dialog("Success", f"PDF Combined Report successfully generated as:\n📁 {filename}")

    def show_alert_dialog(self, title, text):
        alert = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: alert.dismiss())]
        )
        alert.open()

if __name__ == "__main__":
    AcademyApp().run()
