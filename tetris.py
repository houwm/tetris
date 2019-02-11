#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from asciimatics.screen import Screen
from time import sleep
from random import randint
import platform
import copy
import time

sysType = platform.system()
placeholder = 2     # 方块占位（两字符）
compensater = 1     #  DOS补偿位
if sysType == 'Linux':
    compensater = 0
elif sysType == 'Windows':
    pass

iCount = 0              # 出现的块数量 Class:Bar()
iScore = 0              # 得分 int
iTimer = '0 00:00:00'   # 计时
running = False         # 运行状态
pausing = False         # 暂停状态

class Tabtabs(object):
    def __init__(self, type='double'):
        if type == 'single':
            self.horizontal = chr(9472)     # 9472: '─'
            self.vertical = chr(9474)       # 9474: '│'
            self.lefttop = chr(9484)        # 9484: '┌'
            self.righttop = chr(9488)       # 9488: '┐'
            self.leftlower = chr(9492)      # 9492: '└'
            self.rightlower = chr(9496)     # 9496: '┘'
        else:
            self.horizontal = chr(9552)     # 9552: '═'
            self.vertical = chr(9553)       # 9553: '║'
            self.lefttop = chr(9556)        # 9556: '╔'
            self.righttop = chr(9559)       # 9559: '╗'
            self.leftlower = chr(9562)      # 9562: '╚'
            self.rightlower = chr(9565)     # 9565: '╝'

class coordinate(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class block(object):
    def __init__(self, x, y, bg=0, colour=7, char=' ' * placeholder):
        self.x = x
        self.y = y
        self.bg = bg
        self.colour = colour
        self.char = char

class Frame(object):
    def __init__(self, x, y, height, width, tabtabs, printer):
        self.o = coordinate(x, y)   # frame原点坐标
        self.height = height        # 去边后的高度
        self.width = width          # 去边后的宽度，考虑placeholder的倍数处理
        self.printer = printer      # 打印类 Class:myPainter()
        self.__blocks = set()       # 边框绘图元素
        self.__line = [0 for x in range(0, (width) // placeholder)]
        self.canvas = [self.__line[:] for x in range(0, height)]
        #四角
        self.__blocks.add(block(self.o.x, self.o.y, char=tabtabs.lefttop))
        self.__blocks.add(block(self.o.x + width + 1 + compensater, self.o.y, char=tabtabs.righttop))
        self.__blocks.add(block(self.o.x, self.o.y + height + 1, char=tabtabs.leftlower))
        self.__blocks.add(block(self.o.x + width + 1 + compensater, self.o.y + height + 1, char=tabtabs.rightlower))
        #第一行/最后一行
        for ix in range(self.o.x+1, self.o.x+width+1+compensater):
            self.__blocks.add(block(ix, self.o.y, char=tabtabs.horizontal))
            self.__blocks.add(block(ix, self.o.y + height + 1, char=tabtabs.horizontal))
        #第2到n-1行
        for iy in range(self.o.y+1, self.o.y+height+1):
            self.__blocks.add(block(self.o.x, iy, char=tabtabs.vertical))
            self.__blocks.add(block(self.o.x + width + 1 + compensater, iy, char=tabtabs.vertical))
    def paintMe(self):
        self.printer.draw(self.paintData())
    def paintData(self):
        return self.__blocks
    def isNoOut(self, bar):
        postion = bar.postion[:]
        xMax = max(x[0] for x in postion)
        xMin = min(x[0] for x in postion)
        yMax = max(x[1] for x in postion)
        if xMin < 0:                            # 左边界
            return False
        if xMax >= self.width//placeholder:     # 右边界
            return False
        if yMax >= self.height:                 # 下边界
            return False
        # 判断位置重叠
        for x in postion:
            if x[1] > 0:    # Frame上方块的忽略，待进入状态
                if self.canvas[x[1]][x[0]] > 0:
                    return False
        return True
    def clear(self):
        self.canvas = [self.__line[:] for x in range(0, self.height)]
        for i in range(0, self.height):
            myPrinter.print(' '*self.width, self.o.x+1+compensater, self.o.y+i+1, bg=0, colour=0)
    def fixPoints(self, l, c):
        global running
        for x in l:
            if x[1] > 0:
                self.canvas[x[1]][x[0]] = c
            else:
                running = False
                self.printer.setState('Game is OVER!')
        if running:
            self.eliminateLines()
            newBar()
    def eliminateLines(self):
        screen = self.printer.scr
        iRowNum = self.height - 1
        iScores = 0
        while iRowNum > 0:
            row = self.canvas[iRowNum][:]
            if min(x for x in row) > 0:
                screen.print_at(' ' * self.width, self.o.x + 1 + compensater, self.o.y + iRowNum + 1, bg=7)
                screen.refresh()
                sleep(0.02)
                screen.print_at(' ' * self.width, self.o.x + 1 + compensater, self.o.y + iRowNum + 1, bg=0)
                screen.refresh()
                sleep(0.02)
                iScores += 1
                iy = iRowNum
                while iy > 0:
                    self.canvas[iy] = self.canvas[iy - 1][:]
                    for ix in range(0, len(self.canvas[iy - 1])):
                        screen.print_at(' ' * placeholder, self.o.x+ix*placeholder+1+compensater, self.o.y + iy + 1,
                                        bg=self.canvas[iy - 1][ix])
                    iy -= 1
                for ix in range(0, len(self.canvas[0])):
                    self.canvas[0][ix] = 0
                    screen.print_at(' ' * placeholder, self.o.x+ix*placeholder+1+compensater, self.o.y + 1, bg=0)
                screen.refresh()
                iRowNum += 1
            iRowNum -= 1
        self.printer.setScore(7 ** iScores)

class Templet(object):
    __basic = (
        ((0, 0), (0, 1), (0, 2), (0, 3), (1, 3)),
        ((1, 0), (1, 1), (1, 2), (1, 3), (0, 3)),
        ((0, 0), (0, 1), (1, 0), (1, 1)),
        ((0, 0), (0, 1), (0, 2), (0, 3)),
        ((0, 0), (1, 0), (2, 0), (1, 1)),
        ((0, 0), (1, 0), (1, 1), (2, 1)),
        ((0, 1), (1, 1), (1, 0), (2, 0)),
        ((0, 0), (0, 1), (0, 2), (1, 2)),
        ((1, 0), (1, 1), (1, 2), (0, 2)),
    )
    def __init__(self, index, colour=7, rotate=0):
        self.colour = colour
        self.blocks = list()    # class:block 列表
        for el in self.__basic[index]:
            self.blocks.append(list(el))
        for i in range(0, rotate):
            self._rightRotate(self.blocks[1][0], self.blocks[1][1], self.blocks)
        xMin = min(b[0] for b in self.blocks)
        yMin = min(b[1] for b in self.blocks)
        for b in self.blocks:
            b[0] -= xMin
            b[1] -= yMin
    def _leftRotate(self, x0, y0, list):
        for i in range(0, len(list)):
            x1, y1 = list[i][0], list[i][1]
            list[i][0] = x0 + (y1 - y0)
            list[i][1] = y0 - (x1 - x0)
    def _rightRotate(self, x0, y0, list):
        for i in range(0, len(list)):
            x1, y1 = list[i][0], list[i][1]
            list[i][0] = x0 - (y1 - y0)
            list[i][1] = y0 + (x1 - x0)
    def _moveStep(self, x, y, list):
        for i in range(0, len(list)):
            list[i][0] += x
            list[i][1] += y

class Bar(Templet):
    def __init__(self, templet, frame, printer):
        self.blocks = copy.deepcopy(templet.blocks)
        self.colour = templet.colour
        self.myFrame = frame
        self.printer = printer
        self.postion = list()   # 当前位置
        self.ppostion = list()  # 前位置（擦除用）
        for i in range(0, len(self.blocks)):
            self.postion.insert(i, [self.blocks[i][0], self.blocks[i][1]])
    def paintMe(self):
        self.printer.draw(self.paintData(), self.eraseData())
    def moveToBeginPostion(self):
        xMin = min(x[0] for x in self.blocks)
        xMax = max(x[0] for x in self.blocks)
        yMin = min(x[1] for x in self.blocks)
        yMax = max(x[1] for x in self.blocks)
        wFrame = self.myFrame.width // placeholder
        offsetX = randint(0, wFrame - (xMax-xMin+1))
        offsetY = yMax-yMin+1
        for x in self.postion:
            x[0] += offsetX
            x[1] -= offsetY
    def paintData(self):
        s = set()
        for i in range(0, len(self.postion)):
            if self.postion[i][1] >= 0:
                s.add(block((self.postion[i][0]*placeholder)+self.myFrame.o.x+1+compensater, self.postion[i][1]+self.myFrame.o.y+1, bg=self.colour))
        return s
    def eraseData(self):
        s = set()
        for i in range(0, len(self.ppostion)):
            if self.ppostion[i][1] >= 0:
                s.add(block((self.ppostion[i][0]*placeholder)+self.myFrame.o.x+1+compensater, self.ppostion[i][1]+self.myFrame.o.y+1, bg=0, colour=0))
        return s
    def moveLeft(self):
        return self._moveAndDraw('left')
    def moveRight(self):
        return self._moveAndDraw('right')
    def moveDown(self):
        return self._moveAndDraw(('down'))
    def moveDooown(self):
        loop = True
        while loop:
            loop = self.moveDown()
    def rotateLife(self):
        return self._moveAndDraw(('leftRotate'))
    def rotateRight(self):
        return self._moveAndDraw(('rightRotate'))
    def _moveAndDraw(self, direction):
        self.ppostion = copy.deepcopy(self.postion)
        x0 = self.postion[1][0]
        y0 = self.postion[1][1]
        if direction == 'left':
            self._moveStep(-1, 0, self.postion)
        elif direction == 'right':
            self._moveStep(1, 0, self.postion)
        elif direction == 'down':
            self._moveStep(0, 1, self.postion)
        elif direction == 'up':
            self._moveStep(0, -1, self.postion)
        elif direction == 'leftRotate':
            self._leftRotate(x0, y0, self.postion)
        elif direction == 'rightRotate':
            self._rightRotate(x0, y0, self.postion)
        if self.myFrame.isNoOut(self):
            self.paintMe()
            return True
        else:
            self.postion = copy.deepcopy(self.ppostion)
            self.printer.flash(self.paintData())
            if direction == 'down':
                self.myFrame.fixPoints(self.postion[:], self.colour)
            return False

def run(screen):
    global running, pausing, startTime, pauseTime, iScore, iCount
    global myPrinter
    myPrinter = myPainter(screen)
    global mainFrame, activeBar, offsetL, previewFrame, previewBar, myTemplet
    # 初始化主游戏区和活动块
    mainFrame = Frame(0, 0, 32, 28, Tabtabs(), myPrinter)
    myTemplet = Templet(randint(0, 8), randint(1, 6), randint(1, 3))
    activeBar = Bar(myTemplet, mainFrame, myPrinter)
    activeBar.moveToBeginPostion()
    # 屏幕右侧内容位置偏移量
    offsetL = mainFrame.width + 4
    # 初始化预览窗口
    previewFrame = Frame(offsetL, 0, 4, 8, Tabtabs(), myPrinter)
    myTemplet = Templet(randint(0, 8), randint(1, 6), randint(1, 3))
    previewBar = Bar(myTemplet, previewFrame, myPrinter)
    # 绘制游戏区和预览区
    mainFrame.paintMe()
    previewFrame.paintMe()
    previewBar.paintMe()
    # 绘制统计区域
    screen.print_at('timer: ' + iTimer, offsetL+12, 1, colour=7)
    screen.print_at('count: ' + str(iCount), offsetL+12, 2, colour=7)
    screen.print_at('score: ' + str(iScore), offsetL+12, 3, colour=7)
    screen.print_at('state: ready', offsetL+12, 4, colour=7)
    # 绘制操作帮助
    myPrinter.buttonRight(offsetL, 16, 'Q', 'Quit')
    myPrinter.buttonRight(offsetL, 19, 'P', 'Pause')
    myPrinter.buttonRight(offsetL, 22, 'R', 'Resume')
    myPrinter.buttonRight(offsetL, 25, 'N', 'New Game')
    myPrinter.buttonUp(offsetL, 31, 'Z', '↖')
    myPrinter.buttonUp(offsetL + 4, 31, 'X', '↗')
    myPrinter.buttonUp(offsetL + 11, 31, 'M', '↓↓')
    myPrinter.buttonUp(offsetL + 17, 31, 'J', '←')
    myPrinter.buttonUp(offsetL + 21, 31, 'K', '↓')
    myPrinter.buttonUp(offsetL + 25, 31, 'L', '→')

    while True:
        if running and (not pausing):
            refreshTimer()
            activeBar.moveDown()
            sleep(0.2)
        ev = screen.get_key()
        if ev in (ord('Q'), ord('q')):
            return
        elif ev in(ord('N'), ord('n')):
            running = True
            pausing = False
            mainFrame.clear()
            startTime = int(time.time())
            iScore = 0
            iCount = 0
            myPrinter.setScore(0)
            myPrinter.setCount()
            myPrinter.setState('Running...')
        if running:
            if pausing:
                if ev in (ord('R'), ord('r')):
                    pausing = False
                    startTime = startTime + int(time.time()) - pauseTime
                    myPrinter.setState('Running...')
            else:
                if ev in(ord('P'), ord('p')):
                    pausing = True
                    pauseTime = int(time.time())
                    myPrinter.setState('Paused...')
                elif ev in (ord('J'), ord('j')):
                    activeBar.moveLeft()
                elif ev in (ord('L'), ord('l')):
                    activeBar.moveRight()
                elif ev in (ord('K'), ord('k')):
                    activeBar.moveDown()
                elif ev in (ord('M'), ord('m')):
                    activeBar.moveDooown()
                    myPrinter.setScore(3)
                elif ev in (ord('Z'), ord('z')):
                    activeBar.rotateLife()
                elif ev in (ord('X'), ord('x')):
                    activeBar.rotateRight()

class myPainter(object):
    def __init__(self, screen):
        self.scr = screen
    def print(self, char, x, y, bg, colour):
        self.scr.print_at(char, x, y, bg=bg, colour=colour)
    def setTimer(self, t):
        self.scr.print_at(" "*10, mainFrame.width+23, 1)
        self.scr.print_at(t, mainFrame.width+23, 1, colour=7)
        self.scr.refresh()
    def setCount(self):
        global iCount
        iCount += 1
        self.scr.print_at(" "*5, mainFrame.width+23, 2)
        self.scr.print_at(("%d" % iCount), mainFrame.width+23, 2, colour=7)
        self.scr.refresh()
    def setScore(self, i):
        global iScore
        iScore += i
        self.scr.print_at(" "*8, mainFrame.width+23, 3)
        self.scr.print_at(("%d" % iScore), mainFrame.width+23, 3, colour=7)
        self.scr.refresh()
    def setState(self, t):
        self.scr.print_at(" "*13, mainFrame.width+23, 4)
        self.scr.print_at(t, mainFrame.width+23, 4, colour=7)
        self.scr.refresh()
    def buttonRight(self, x, y, key, comment):
        Frame(x, y, 1, 1, Tabtabs('single'), myPrinter).paintMe()
        self.scr.print_at(key, x+1+compensater, y+1, colour=7)
        self.scr.print_at(comment, x+3+compensater*2, y+1, colour=7)
        self.scr.refresh()
    def buttonUp(self, x, y, key, comment):
        Frame(x, y, 1, 1, Tabtabs('single'), myPrinter).paintMe()
        self.scr.print_at(key, x+1+compensater, y+1, colour=7)
        self.scr.print_at(comment, x+1, y-1, colour=7)
        self.scr.refresh()
    def flash(self, bs):
        for i in range(0, 2):
            for d in bs:
                self.scr.print_at(d.char, d.x, d.y, bg=7, colour=7)
                self.scr.refresh()
            sleep(0.04)
            for d in bs:
                self.scr.print_at(d.char, d.x, d.y, bg=d.bg, colour=d.colour)
                self.scr.refresh()
            sleep(0.02)
    def draw(self, data, eraseData=None):
        if eraseData:
            for d in eraseData:
                self.scr.print_at(d.char, d.x, d.y, bg=0, colour=0)
        for d in data:
            self.scr.print_at(d.char, d.x, d.y, bg=d.bg, colour=d.colour)
        self.scr.refresh()

def newBar():
    global activeBar, previewBar, mainFrame, previewFrame, myPrinter, myTemplet
    activeBar = Bar(myTemplet, mainFrame, myPrinter)
    activeBar.moveToBeginPostion()
    myTemplet = Templet(randint(0, 8), randint(1, 6), randint(1, 3))
    previewFrame.clear()
    previewBar = Bar(myTemplet, previewFrame, myPrinter)
    previewBar.paintMe()
    myPrinter.setCount()

def refreshTimer():
    global startTime, myPrinter
    _now = int(time.time()) - startTime
    _day = _now // (60*60*24)
    _hour = _now % (60*60*24) // (60*60)
    _minute = _now % (60*60) // 60
    _second = _now % 60
    ti = '%d %02d:%02d:%02d' % (_day, _hour, _minute, _second)
    myPrinter.setTimer(ti)

startTime = int(time.time())
Screen.wrapper(run)