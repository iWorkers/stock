import os
import time
import requests
import json
from PyQt6.QtCore import *
from PyQt6 import *
import sys
from PyQt6.QtWidgets import *
from stockui import Ui_MainWindow
from PyQt6.QtGui import *

class SystemTray(object):
    # 程序托盘类
    def __init__(self,w):
        self.app = app
        self.w = w
        
        self.w.show()  # 不设置显示则为启动最小化到托盘
        self.tp = QSystemTrayIcon(self.w)
        self.initUI()
        self.run()

    def initUI(self):
        # 设置托盘图标

        self.tp.setIcon(QIcon('./ico.ico'))

    def quitApp(self):
        # 退出程序
        self.w.hide()  # w.hide() #设置退出时是否显示主窗口
        self.tp=None # 隐藏托盘控件，托盘图标刷新不及时，提前隐藏
        self.app.quit()  # 退出程序
    def addstock(self):
        text, ok = QInputDialog.getText(self.w, '添加自选', '股票代码：')
        if ok:
            #v_pv_none_match="1";
            if str(text).startswith('00',0 ,2) or str(text).startswith('30',0 ,2):
                zf='sz'
            elif str(text).startswith('60',0 ,2) or str(text).startswith('68',0 ,2):
                zf='sh'
            URL=f'http://qt.gtimg.cn/q=s_{zf}{text}'
            result=requests.get(URL).text
            if not('none_match' in result) :
                
                #print(self.w.daima.values())
                if text in self.w.daima.values():
                    print("YES")
                else:
                    dict2 ={text: text}
                    self.w.daima.update(dict2)
                with open("./stock.json", 'w', encoding='utf-8') as fw:
                    json.dump(self.w.daima, fw, indent=4, ensure_ascii=False)
            else :
                print('股票不存在')
    def outstock(self) :
        items = self.w.daima.values()
        
        item ,ok = QInputDialog.getItem(self.w,"删除自选",'选择股票代码',items,0,False)
        if ok and item:
            #print(list(items).index(item))
            self.w.daima.pop(item)
            
            with open("./stock.json", 'w', encoding='utf-8') as fw:
                json.dump(self.w.daima, fw, indent=4, ensure_ascii=False)
            
    def hideIco(self):
        # 退出程序
        if not self.w.isVisible():
            self.w.show()
        
        self.tp.setVisible(False)  # 隐藏托盘控件，托盘图标刷新不及时，提前隐藏
       
    def hideWin(self):
        if not self.w.isVisible():
            self.w.show()
        else :
            self.w.hide()

    def act(self, reason):
        # 主界面显示方法
        # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击
        
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick :
           
            if self.w.isVisible():
                self.w.hide()
            else :
                self.w.show()
        elif reason == QSystemTrayIcon.ActivationReason.Context :
            a5 = QAction('&添加自选', triggered=self.addstock)
            a1 = QAction('&删除自选', triggered=self.outstock)
            a4 = QAction('&显示/隐藏', triggered=self.hideWin)
            
            a3 = QAction('&隐藏图标', triggered=self.hideIco)
            a2 = QAction('&退出', triggered=self.quitApp)

            self.tpMenu = QMenu()
            self.tpMenu.addAction(a5)
            self.tpMenu.addAction(a1)
            self.tpMenu.addAction(a4)
            
            self.tpMenu.addAction(a3)
            self.tpMenu.addAction(a2)
            self.tp.setContextMenu(self.tpMenu)
            rect = self.tp.geometry()
            hi = self.tpMenu.sizeHint().height()-15
            self.tp.contextMenu().exec(QPoint(rect.left()+20,rect.top()-hi))
            
    def run(self):

  
        self.tp.show()  # 不调用show不会显示系统托盘消息，图标隐藏无法调用
        #self.tp.messageClicked.connect(self.message)
        # 绑定托盘菜单点击事件
        self.tp.activated.connect(self.act)
        


class MainWin(QMainWindow, Ui_MainWindow):
   
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._tracking = False
        # 获取屏幕坐标系
        screen =  QGuiApplication.primaryScreen().geometry() 
        # 获取窗口坐标系
        size = self.tableWidget.geometry()
        newLeft = screen.width() - size.width()
        newTop = 0
        self.move(newLeft,newTop)

        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 窗体背景透明
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)  #窗口置顶，无边框，在任务栏不显示图标
        self.tableWidget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.setStyleSheet("background-color:rgba(0,0,0,0)")
        self.tableWidget.horizontalHeader().setStyleSheet("QHeaderView::section {background-color:rgba(0,0,0,0);color: red;}")

        self.tableWidget.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tableWidget.setShowGrid(False)
        self.tableWidget.setFrameShape(QFrame.Shape.NoFrame)
        
        self.tableWidget.horizontalHeader().viewport().installEventFilter(self)
        self.tableWidget.viewport().installEventFilter(self)
        


        
        self.tableWidget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tableWidget.setWindowOpacity(0.9)
        
        
        with open("stock.json", 'r', encoding='utf-8') as fw:
            self.daima = json.load(fw)
        self.my_thread = Mythread()
        self.my_thread.setPath(self.daima)
        self.my_thread.my_signal.connect(self.set_label_func)
        
        self.my_thread.start()
        self.tray() # 程序实现托盘
       
        
    def tray(self):
        # 创建托盘程序
        self.ti = SystemTray(self)
        
        self.tableWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu) # 允许右键产生子菜单
        self.tableWidget.customContextMenuRequested.connect(self.tableWidget_VTest_menu)  # 右键菜单
        #sys.exit(self.ti.app.exec())

        
    def tableWidget_VTest_menu(self, pos):
        menu = QMenu() #实例化菜单
        item1 = menu.addAction(u"显示/隐藏图标")
        
        action = menu.exec(self.tableWidget.mapToGlobal(pos))
        
        if action == item1:
            if self.ti.tp.isVisible():
                self.ti.tp.setVisible(False)
            else :
                self.ti.tp.setVisible(True)
        
            

    
    def eventFilter(self, watched, event):
        
        if event.type()==2 and event.buttons()==Qt.MouseButton.LeftButton: #MouseButtonPress
            self._tracking = True
            self._startPos=event.pos()
            return True
        if event.type()==5 and self._tracking: #MouseMove
            self._endPos = event.pos() - self._startPos
            self.move(self.pos() + self._endPos)
            return True
        if event.type()==3 : #MouseButtonRelease  and event.buttons()==Qt.MouseButton.LeftButton
            
            self._tracking = False
            self._startPos = None
            self._endPos = None
            return True
        return super(MainWin, self).eventFilter(watched, event) 
    
    '''
    def mouseMoveEvent(self, a0):
        print(a0.pos())
 
        if self._tracking:
            self._endPos = a0.pos() - self._startPos
            self.move(self.pos() + self._endPos)
            
	    
    def mousePressEvent(self, a0):
        if a0.buttons()==Qt.MouseButton.LeftButton:
            self._tracking = True
            self._startPos=a0.pos()
            
  
    def mouseReleaseEvent(self, a0):
        if a0.buttons() == Qt.MouseButton.LeftButton:
            self._tracking = False
            self._startPos = None
            self._endPos = None
    '''
  

   
    def set_label_func(self, arryyy):  # 4
        x = 0
        self.isexit = False
        row_count = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(len(arryyy))
        if row_count>0 :
            self.isexit = True
        
        for i in arryyy:
            if not self.isexit:
                row_count = self.tableWidget.rowCount()  # 返回当前行数(尾部)
                self.tableWidget.insertRow(row_count)  # 尾部插入一行
            l=str(i).split('~')
            item1 =QTableWidgetItem(l[1])
            item2 =QTableWidgetItem(l[2])
            item3 =QTableWidgetItem(l[3])
            item4 =QTableWidgetItem(l[4])
            item5 =QTableWidgetItem(l[5])
            item6 =QTableWidgetItem(l[6])
           
            if "-" in l[4]:
                item1.setForeground(QColor(0,255,0))
                item2.setForeground(QColor(0,255,0))
                item3.setForeground(QColor(0,255,0))
                item4.setForeground(QColor(0,255,0))
                item5.setForeground(QColor(0,255,0))
                item6.setForeground(QColor(0,255,0))
            else :
                item1.setForeground(QColor(255,0,0))
                item2.setForeground(QColor(255,0,0))
                item3.setForeground(QColor(255,0,0))
                item4.setForeground(QColor(255,0,0))
                item5.setForeground(QColor(255,0,0))
                item6.setForeground(QColor(255,0,0))
            self.tableWidget.setItem(arryyy.index(i),1,item1)
            self.tableWidget.setItem(arryyy.index(i),0,item2)
            self.tableWidget.setItem(arryyy.index(i),2,item3)
            self.tableWidget.setItem(arryyy.index(i),3,item4)
            self.tableWidget.setItem(arryyy.index(i),4,item5)
            self.tableWidget.setItem(arryyy.index(i),5,item6)
            
            x = x + 1
           

class Mythread(QThread):
    #声明一个信号，同时返回一个int，什么都可以返回，参数是发送信号时附带参数的数据类型
    my_signal = pyqtSignal(list) 
    def __init__(self):
        super(Mythread, self).__init__()
        self.filepath = ''
    
     
    def setPath(self,path):
        self.filepath = path
        
    def run(self):
        while True:
            
            arr=[]
            for key, value in self.filepath.items():
                
                if value.startswith('00',0 ,2) or value.startswith('30',0 ,2):
                    zf='sz'
                elif value.startswith('60',0 ,2) or value.startswith('68',0 ,2):
                    zf='sh'
                URL=f'http://qt.gtimg.cn/q=s_{zf}{value}'
                result=requests.get(URL).text
                arr.append(result)
            self.my_signal.emit(arr)
            
            time.sleep(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWin()
    
    
    main_win.show()
    sys.exit(app.exec())
    '''
    while True:
        t=Thread(target=work)
        t.start()
        print('主线程/主进程')
        time.sleep(1)
        
   '''
