import sys
import json
import os
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QScrollArea, 
                             QFrame, QMenu, QStackedWidget, QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal, QObject, QByteArray, QBuffer, QIODevice
from PyQt6.QtGui import QFont, QCursor, QColor, QAction, QImage, QPixmap
import keyboard
from PyQt6.QtGui import QIcon

# Cores
BG_COLOR = "#0A0A0A"
PANEL_COLOR = "#141414"
CARD_COLOR = "#1A1A1A"
ACCENT_COLOR = "#00D15E"
TEXT_COLOR = "#E0E0E0"
MUTED_COLOR = "#888888"

class SignalEmitter(QObject):
    paste_requested = pyqtSignal(int)

class TitleBar(QFrame):
    def __init__(self, parent, menu_callback):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(50)
        self.setStyleSheet(f"background-color: {BG_COLOR}; border: none;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Logo
        logo_label = QLabel()
        logo_label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 18px; font-weight: bold; border: none;")
        logo_label.setFont(QFont("Segoe UI"))
        logo_text = f'<span style="color: {ACCENT_COLOR};">&gt;_</span> <span style="color: {TEXT_COLOR};">ClipMaster</span>'
        logo_label.setText(logo_text)
        
        # Menu Button
        self.menu_btn = QPushButton("Menu ▼")
        self.menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_btn.setStyleSheet(f"""
            QPushButton {{ color: {TEXT_COLOR}; background: transparent; border: none; font-size: 14px; font-family: 'Segoe UI'; }}
            QPushButton:hover {{ color: {ACCENT_COLOR}; }}
        """)
        self.menu_btn.clicked.connect(menu_callback)

        # --- Minimize Button ---
        self.minimize_btn = QPushButton("➖")
        self.minimize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.minimize_btn.setStyleSheet(f"""
            QPushButton {{ color: {MUTED_COLOR}; background: transparent; border: none; font-size: 12px; }}
            QPushButton:hover {{ color: #E0E0E0; }}
        """)
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        
        # Close Button
        close_btn = QPushButton("✕")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{ color: {MUTED_COLOR}; background: transparent; border: none; font-size: 14px; padding-left: 10px; }}
            QPushButton:hover {{ color: #FF4444; }}
        """)
        close_btn.clicked.connect(self.parent.close)
        
        layout.addWidget(logo_label)
        layout.addStretch()
        layout.addWidget(self.menu_btn)
        layout.addWidget(self.minimize_btn)
        layout.addWidget(close_btn)
        
        self.startPos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.startPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.startPos:
            delta = event.globalPosition().toPoint() - self.startPos
            self.parent.move(self.parent.pos() + delta)
            self.startPos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.startPos = None

class ClipCard(QFrame):
    def __init__(self, index, item, copy_callback, delete_callback):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{ background-color: {CARD_COLOR}; border: 1px solid #2A2A2A; border-radius: 8px; margin-bottom: 10px; }}
            QFrame:hover {{ border: 1px solid {ACCENT_COLOR}; }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Top row: Badge and Icons
        top_layout = QHBoxLayout()
        badge = QLabel(f"Alt+Shift+{index}")
        badge.setStyleSheet(f"""
            background-color: rgba(0, 230, 118, 0.1); color: {ACCENT_COLOR}; border-radius: 12px;
            padding: 4px 10px; font-size: 11px; font-weight: bold; font-family: 'Consolas'; border: none;
        """)
        top_layout.addWidget(badge)
        top_layout.addStretch()
        
        copy_btn = QPushButton("📋")
        copy_btn.setToolTip("Copiar de volta para a área de transferência")
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {MUTED_COLOR}; border: none; font-size: 14px; padding: 0 5px; }} QPushButton:hover {{ color: {TEXT_COLOR}; }}")
        copy_btn.clicked.connect(lambda: copy_callback(item))
        
        del_btn = QPushButton("🗑️")
        del_btn.setToolTip("Excluir este item")
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {MUTED_COLOR}; border: none; font-size: 14px; padding: 0 5px; }} QPushButton:hover {{ color: #FF4444; }}")
        del_btn.clicked.connect(lambda: delete_callback(index))
        
        top_layout.addWidget(copy_btn)
        top_layout.addWidget(del_btn)
        
        layout.addLayout(top_layout)
        
        # Content
        if item["type"] == "text":
            display_text = item["data"].replace('\n', ' ')
            if len(display_text) > 80: display_text = display_text[:77] + "..."
            text_label = QLabel(display_text)
            text_label.setWordWrap(True)
            text_label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 13px; font-family: 'Segoe UI'; border: none; margin-top: 8px;")
            layout.addWidget(text_label)
        elif item["type"] == "image":
            ba = QByteArray.fromBase64(item["data"].encode())
            pixmap = QPixmap()
            pixmap.loadFromData(ba, "PNG")
            img_label = QLabel()
            scaled_pixmap = pixmap.scaled(250, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            img_label.setPixmap(scaled_pixmap)
            img_label.setStyleSheet("border: 1px solid #333; border-radius: 4px; margin-top: 8px;")
            layout.addWidget(img_label)

class SessionCard(QFrame):
    def __init__(self, name, items, load_cb, delete_cb):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{ background-color: {CARD_COLOR}; border: 1px solid #2A2A2A; border-radius: 8px; margin-bottom: 10px; }}
            QFrame:hover {{ border: 1px solid {ACCENT_COLOR}; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        top_layout = QHBoxLayout()
        title = QLabel(f"📁 {name}")
        title.setStyleSheet(f"color: {ACCENT_COLOR}; font-weight: bold; font-size: 14px; border: none;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        btn_style = f"QPushButton {{ background: transparent; color: {MUTED_COLOR}; border: none; font-size: 14px; padding: 0 5px; }} QPushButton:hover {{ color: {TEXT_COLOR}; }}"
        
        load_btn = QPushButton("📂 Carregar")
        load_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        load_btn.setStyleSheet(btn_style)
        load_btn.clicked.connect(lambda: load_cb(name))
        
        del_btn = QPushButton("🗑️")
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet(btn_style + "QPushButton:hover { color: #FF4444; }")
        del_btn.clicked.connect(lambda: delete_cb(name))
        
        top_layout.addWidget(load_btn)
        top_layout.addWidget(del_btn)
        layout.addLayout(top_layout)
        
        count_label = QLabel(f"{len(items)} itens salvos nesta sessão")
        count_label.setStyleSheet(f"color: {MUTED_COLOR}; font-size: 12px; border: none; margin-top: 5px;")
        layout.addWidget(count_label)

class ClipMasterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.resize(450, 650)
        self.setStyleSheet(f"background-color: {BG_COLOR};")
        self.setWindowIcon(QIcon('icone.ico'))
        
        self.current_session = []
        self.sessions = {}
        self.session_file = "clipmaster_data.json"
        
        self.signals = SignalEmitter()
        self.signals.paste_requested.connect(self.execute_paste)
        
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard_change)
        self.ignore_clipboard = False
        
        self.load_data()
        self.setup_ui()
        self.setup_hotkeys()

    def load_data(self):
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sessions = data.get("sessions", {})
            except:
                self.sessions = {}

    def save_data(self):
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump({"sessions": self.sessions}, f, ensure_ascii=False, indent=4)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.title_bar = TitleBar(self, self.show_menu)
        main_layout.addWidget(self.title_bar)
        
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        self.page_current = self.create_scroll_page("📋 CLIPBOARD ATUAL", is_current=True)
        self.page_saved = self.create_scroll_page("💾 SESSÕES SALVAS")
        self.page_shortcuts = self.create_shortcuts_page()
        
        self.stacked_widget.addWidget(self.page_current['widget'])
        self.stacked_widget.addWidget(self.page_saved['widget'])
        self.stacked_widget.addWidget(self.page_shortcuts)
        
        self.update_current_ui()
        self.update_saved_ui()

    def create_scroll_page(self, title_text, is_current=False):
        page = QWidget()
        page.setStyleSheet(f"background-color: {PANEL_COLOR};")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel(title_text)
        title.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 16px; font-weight: bold; font-family: 'Segoe UI'; letter-spacing: 1px; margin-bottom: 10px;")
        layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background-color: transparent; }}
            QScrollBar:vertical {{ background: {BG_COLOR}; width: 8px; border-radius: 4px; }}
            QScrollBar::handle:vertical {{ background: #333; border-radius: 4px; }}
            QScrollBar::handle:vertical:hover {{ background: {ACCENT_COLOR}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        if is_current:
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(0, 10, 0, 0)
            
            btn_save = QPushButton("💾 Salvar Sessão")
            btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_save.setStyleSheet(f"QPushButton {{ background-color: {ACCENT_COLOR}; color: black; font-weight: bold; padding: 10px; border-radius: 4px; border: none; }} QPushButton:hover {{ background-color: #00C853; }}")
            btn_save.clicked.connect(self.save_current_session)
            
            btn_clear = QPushButton("🗑️ Limpar")
            btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_clear.setStyleSheet(f"QPushButton {{ background-color: #333; color: white; font-weight: bold; padding: 10px; border-radius: 4px; border: none; }} QPushButton:hover {{ background-color: #444; }}")
            btn_clear.clicked.connect(self.clear_current_session)
            
            btn_layout.addWidget(btn_save)
            btn_layout.addWidget(btn_clear)
            layout.addLayout(btn_layout)
        
        return {'widget': page, 'layout': content_layout}

    def create_shortcuts_page(self):
        page = QWidget()
        page.setStyleSheet(f"background-color: {PANEL_COLOR};")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        title = QLabel("⌨️ ATALHOS E AJUDA")
        title.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 16px; font-weight: bold; font-family: 'Segoe UI'; margin-bottom: 20px;")
        layout.addWidget(title)
        
        info = QLabel(
            "<b>Como usar:</b><br><br>"
            "1. Copie textos ou imagens normalmente usando <b>Ctrl+C</b>.<br>"
            "2. O ClipMaster armazena os últimos 10 itens copiados na Sessão Atual.<br>"
            "3. Para colar um item específico, use os atalhos abaixo:<br><br>"
            f"<span style='color:{ACCENT_COLOR};'>Alt + Shift + 0</span> : Cola o último item copiado<br>"
            f"<span style='color:{ACCENT_COLOR};'>Alt + Shift + 1</span> : Cola o penúltimo item<br>"
            "... e assim por diante até o 9.<br><br>"
            "<b>Sessões (Abas):</b><br>"
            "Você pode salvar todos os itens da tela atual como uma 'Sessão' nomeada. "
            "Isso permite limpar o clipboard para um novo trabalho e depois carregar a sessão antiga de volta."
        )
        info.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 14px; line-height: 1.5;")
        info.setWordWrap(True)
        layout.addWidget(info)

        # --- CRÉDITOS ---
        layout.addStretch()
        
        credits_label = QLabel(
            "<div style='text-align: center; color: #888888; font-size: 13px; margin-top: 20px;'>"
            "Criado por <b>Paulo Almeida</b><br>"
            "<a href='https://github.com/Almeida-Paulo/clipmaster' style='color: #00E676; text-decoration: none;'>"
            "github.com/Almeida-Paulo/clipmaster</a>"
            "</div>"
        )
        credits_label.setOpenExternalLinks(True) 
        layout.addWidget(credits_label)
        # --------------------------
        
        return page

    def show_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background-color: {CARD_COLOR}; color: {TEXT_COLOR}; border: 1px solid #333; border-radius: 4px; padding: 5px 0; }}
            QMenu::item {{ padding: 8px 25px; font-family: 'Segoe UI'; font-size: 13px; }}
            QMenu::item:selected {{ background-color: #2A2A2A; color: {ACCENT_COLOR}; }}
        """)
        
        act_current = QAction("Clipboard Atual", self)
        act_current.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        act_saved = QAction("Sessões Salvas", self)
        act_saved.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        act_shortcuts = QAction("Atalhos e Ajuda", self)
        act_shortcuts.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        
        menu.addAction(act_current)
        menu.addAction(act_saved)
        menu.addAction(act_shortcuts)
        
        pos = self.title_bar.menu_btn.mapToGlobal(QPoint(0, self.title_bar.menu_btn.height()))
        menu.exec(pos)

    def setup_hotkeys(self):
        keyboard.unhook_all()
        for i in range(10):
            keyboard.add_hotkey(f"alt+shift+{i}", lambda idx=i: self.signals.paste_requested.emit(idx), suppress=True)

    def on_clipboard_change(self):
        if self.ignore_clipboard:
            return
            
        mime = self.clipboard.mimeData()
        item = None
        
        if mime.hasImage():
            img = self.clipboard.image()
            if not img.isNull():
                ba = QByteArray()
                buf = QBuffer(ba)
                buf.open(QIODevice.OpenModeFlag.WriteOnly)
                img.save(buf, "PNG")
                item = {"type": "image", "data": ba.toBase64().data().decode()}
        elif mime.hasText():
            txt = mime.text()
            if txt.strip():
                item = {"type": "text", "data": txt}
                
        if item:
            if not self.current_session or self.current_session[0] != item:
                self.current_session.insert(0, item)
                if len(self.current_session) > 10:
                    self.current_session.pop()
                self.update_current_ui()

    def update_current_ui(self):
        layout = self.page_current['layout']
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        if not self.current_session:
            empty_label = QLabel("Nenhum item copiado ainda.")
            empty_label.setStyleSheet(f"color: {MUTED_COLOR}; font-style: italic;")
            layout.addWidget(empty_label)
        else:
            for i, item in enumerate(self.current_session):
                card = ClipCard(i, item, self.manual_copy, self.delete_item)
                layout.addWidget(card)
                
        layout.addStretch()

    def manual_copy(self, item):
        self.ignore_clipboard = True
        if item["type"] == "text":
            self.clipboard.setText(item["data"])
        elif item["type"] == "image":
            ba = QByteArray.fromBase64(item["data"].encode())
            img = QImage.fromData(ba, "PNG")
            self.clipboard.setImage(img)
        QTimer.singleShot(500, self.reset_ignore_clipboard)

    def save_current_session(self):
        if not self.current_session:
            QMessageBox.warning(self, "Aviso", "A sessão atual está vazia!")
            return
            
        name, ok = QInputDialog.getText(self, "Salvar Sessão", "Nome da sessão (ex: Pesquisa Faculdade):")
        if ok and name.strip():
            name = name.strip()
            self.sessions[name] = self.current_session.copy()
            self.save_data()
            self.update_saved_ui()
            self.title_bar.menu_btn.setText("Salvo! ▼")
            QTimer.singleShot(2000, lambda: self.title_bar.menu_btn.setText("Menu ▼"))

    def clear_current_session(self):
        self.current_session = []
        self.update_current_ui()

    def delete_item(self, index):
        if 0 <= index < len(self.current_session):
            self.current_session.pop(index)
            self.update_current_ui()

    def load_session(self, name):
        if name in self.sessions:
            self.current_session = self.sessions[name].copy()
            self.update_current_ui()
            self.stacked_widget.setCurrentIndex(0)

    def delete_session(self, name):
        if name in self.sessions:
            reply = QMessageBox.question(self, "Confirmar", f"Excluir a sessão '{name}'?", 
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                del self.sessions[name]
                self.save_data()
                self.update_saved_ui()

    def update_saved_ui(self):
        layout = self.page_saved['layout']
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        if not self.sessions:
            empty_label = QLabel("Nenhuma sessão salva.")
            empty_label.setStyleSheet(f"color: {MUTED_COLOR}; font-style: italic;")
            layout.addWidget(empty_label)
        else:
            for name, items in self.sessions.items():
                card = SessionCard(name, items, self.load_session, self.delete_session)
                layout.addWidget(card)
                
        layout.addStretch()

    def execute_paste(self, index):
        if index < len(self.current_session):
            item = self.current_session[index]
            self.manual_copy(item)
            time.sleep(0.1)
            keyboard.send('ctrl+v')

    def reset_ignore_clipboard(self):
        self.ignore_clipboard = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Dialogs Global Styles (QInputDialog, QMessageBox)
    app.setStyleSheet(f"""
        QMessageBox, QInputDialog {{ background-color: {BG_COLOR}; color: {TEXT_COLOR}; }}
        QLabel {{ color: {TEXT_COLOR}; }}
        QLineEdit {{ background-color: {CARD_COLOR}; color: {TEXT_COLOR}; border: 1px solid {ACCENT_COLOR}; padding: 5px; }}
        QPushButton {{ background-color: {CARD_COLOR}; color: {TEXT_COLOR}; border: 1px solid #333; padding: 5px 15px; border-radius: 4px; }}
        QPushButton:hover {{ border: 1px solid {ACCENT_COLOR}; color: {ACCENT_COLOR}; }}
    """)
    
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = ClipMasterApp()
    window.show()
    sys.exit(app.exec())
