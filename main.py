"""SimpleMailGUI 入口：負責啟動 CustomTkinter 主視窗。"""

from ui import MainWindow

if __name__ == "__main__":
    # 建立主視窗並啟動事件迴圈
    app = MainWindow()
    app.mainloop()
