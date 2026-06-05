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
from datetime import datetime
import os
import database

# Export Libraries
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

KV = '''
MDScreen:
    MDBoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            title: "Mallakhamb Academy"
            elevation: 4
            right_action_items: [["theme-light-dark", lambda x: app.toggle_theme()]]

        MDBottomNavigation:
            panel_color: app.theme_cls.bg_dark
            
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

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepOrange"
        database.create_tables()
        return Builder.load_string(KV)

    def on_start(self):
        self.load_students()
        today_str = datetime.now().strftime("%B %d, %Y")
        self.root.ids.attendance_date_label.text = f"Attendance: {today_str}"

    def toggle_theme(self):
        self.theme_cls.theme_style = "Light" if self.theme_cls.theme_style == "Dark" else "Dark"

    def load_students(self, *args):
        self.root.ids.student_list.clear_widgets()
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, phone FROM students")
        students = cursor.fetchall()
        conn.close()
        
        for student in students:
            student_id, name, phone = student
            item = TwoLineAvatarIconListItem(text=name, secondary_text=f"Phone: {phone}")
            avatar = ImageLeftWidget(source="assets/logo.png")
            item.add_widget(avatar)
            self.root.ids.student_list.add_widget(item)

    def show_add_student_dialog(self):
        self.name_field = MDTextField(hint_text="Student Name")
        self.phone_field = MDTextField(hint_text="Phone Number")
        
        dialog_layout = MDBoxLayout(orientation="vertical", spacing="12dp", size_hint_y=None, height="120dp")
        dialog_layout.add_widget(self.name_field)
        dialog_layout.add_widget(self.phone_field)

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

    def save_student(self, *args):
        name = self.name_field.text
        phone = self.phone_field.text
        if name:
            conn = database.connect()
            cursor = conn.cursor()
            today_date = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("INSERT INTO students (name, phone, join_date) VALUES (?, ?, ?)", (name, phone, today_date))
            conn.commit()
            conn.close()
            self.dialog.dismiss()
            self.load_students()

    def load_attendance_list(self, *args):
        self.root.ids.attendance_list.clear_widgets()
        today = datetime.now().strftime("%Y-%m-%d")
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM students")
        students = cursor.fetchall()
        
        for student in students:
            student_id, name = student
            cursor.execute("SELECT status FROM attendance WHERE student_id = ? AND date = ?", (student_id, today))
            row = cursor.fetchone()
            status = row[0] if row else "Absent"
            
            item = TwoLineAvatarIconListItem(text=name, secondary_text=f"Today's Status: {status}")
            avatar = ImageLeftWidget(source="assets/logo.png")
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
        if cursor.fetchone():
            cursor.execute("UPDATE attendance SET status = ? WHERE student_id = ? AND date = ?", (new_status, student_id, today))
        else:
            cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)", (student_id, today, new_status))
        conn.commit()
        conn.close()
        self.load_attendance_list()

    def export_attendance_excel(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Attendance Logs"
        ws.append(["Record ID", "Student Name", "Date Label", "Status"])
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT a.id, s.name, a.date, a.status FROM attendance a JOIN students s ON a.student_id = s.id ORDER BY a.date DESC")
        for row in cursor.fetchall():
            ws.append(row)
        conn.close()
        
        # Save securely to internal storage on mobile devices
        filename = "Attendance_Report.xlsx"
        if os.name != 'nt': 
            from android.storage import app_storage_path
            filename = os.path.join(app_storage_path(), filename)
            
        wb.save(filename)
        self.show_alert_dialog("Success", f"Excel report saved successfully to storage.")

    def export_student_pdf(self):
        filename = "Academy_Roster_Attendance.pdf"
        if os.name != 'nt':
            from android.storage import app_storage_path
            filename = os.path.join(app_storage_path(), filename)
            
        c = canvas.Canvas(filename, pagesize=letter)
        today = datetime.now().strftime("%Y-%m-%d")
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, 750, "Mallakhamb Academy")
        c.setFont("Helvetica", 12)
        c.drawString(50, 730, f"Comprehensive Roster & Attendance — Run Date: {today}")
        c.line(50, 715, 550, 715)
        
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT s.id, s.name, s.phone, COALESCE(a.status, 'Absent') FROM students s LEFT JOIN attendance a ON s.id = a.student_id AND a.date = ?", (today,))
        dataset = cursor.fetchall()
        conn.close()
        
        y_position = 650
        for record in dataset:
            student_id, name, phone, status = record
            c.setFont("Helvetica", 10)
            c.drawString(60, y_position, str(student_id))
            c.drawString(100, y_position, name)
            c.drawString(280, y_position, str(phone))
            if status == "Present":
                c.setFont("Helvetica-Bold", 10)
            c.drawString(430, y_position, status)
            y_position -= 25
        c.save()
        self.show_alert_dialog("Success", "PDF report saved successfully to storage.")

    def show_alert_dialog(self, title, text):
        alert = MDDialog(title=title, text=text, buttons=[MDFlatButton(text="OK", on_release=lambda x: alert.dismiss())])
        alert.open()

if __name__ == "__main__":
    AcademyApp().run()
