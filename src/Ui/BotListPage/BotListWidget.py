# -*- coding: utf-8 -*-

"""
机器人列表
"""
from abc import ABC
from typing import TYPE_CHECKING, Self, Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from creart import add_creator, exists_module, it
from creart.creator import AbstractCreator, CreateTargetInfo

from src.Ui.BotListPage.BotList import BotList
from src.Ui.BotListPage.BotTopCard import BotTopCard
from src.Ui.StyleSheet import StyleSheet

if TYPE_CHECKING:
    from src.Ui.MainWindow import MainWindow


class BotListWidget(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.view: Optional[QStackedWidget] = None
        self.topCard: Optional[BotTopCard] = None
        self.botList: Optional[BotList] = None
        self.vBoxLayout: Optional[QVBoxLayout] = None

    def initialize(self, parent: "MainWindow") -> Self:
        """
        初始化
        """
        self.vBoxLayout = QVBoxLayout(self)

        self.topCard = BotTopCard(self)
        self.view = QStackedWidget(self)
        self.botList = BotList(self.view)

        # 设置 QWidget
        self.setParent(parent),
        self.setObjectName("BotListPage")
        self.view.setObjectName("BotListStackedWidget")
        self.view.addWidget(self.botList)
        self.view.setCurrentWidget(self.botList)

        # 调用方法
        self._setLayout()

        # 应用样式表
        StyleSheet.BOT_LIST_WIDGET.apply(self)

        return self

    def _setLayout(self) -> None:
        """
        ## 对内部进行布局
        """
        self.vBoxLayout.addWidget(self.topCard)
        self.vBoxLayout.addWidget(self.view)
        self.vBoxLayout.setContentsMargins(24, 20, 24, 10)
        self.setLayout(self.vBoxLayout)

    def stopAllBot(self):
        """
        ## 停止所有 bot
        """
        for bot in self.botList.botCardList:
            if not bot.botWidget:
                continue
            if bot.botWidget.isRun:
                bot.botWidget.stopButton.click()

    def getBotIsRun(self):
        """
        ## 获取是否有 bot 正在运行
        """
        for bot in self.botList.botCardList:
            if not bot.botWidget:
                # 如果没有创建则表示没有运行
                continue
            if bot.botWidget.isRun:
                return True

    def showInfo(self, title: str, content: str) -> None:
        """
        # 配置 InfoBar 的一些配置, 简化内部使用 InfoBar 的步骤
        """
        from src.Ui.MainWindow.Window import MainWindow
        it(MainWindow).showInfo(
            title=title,
            content=content,
            showcasePage=self
        )

    def showError(self, title: str, content: str) -> None:
        """
        # 配置 InfoBar 的一些配置, 简化内部使用 InfoBar 的步骤
        """
        from src.Ui.MainWindow.Window import MainWindow
        it(MainWindow).showError(
            title=title,
            content=content,
            showcasePage=self
        )

    def showWarning(self, title: str, content: str) -> None:
        """
        # 配置 InfoBar 的一些配置, 简化内部使用 InfoBar 的步骤
        """
        from src.Ui.MainWindow.Window import MainWindow
        it(MainWindow).showWarning(
            title=title,
            content=content,
            showcasePage=self
        )

    def showSuccess(self, title: str, content: str) -> None:
        """
        # 配置 InfoBar 的一些配置, 简化内部使用 InfoBar 的步骤
        """
        from src.Ui.MainWindow.Window import MainWindow
        it(MainWindow).showSuccess(
            title=title,
            content=content,
            showcasePage=self
        )


class BotListWidgetClassCreator(AbstractCreator, ABC):
    # 定义类方法targets，该方法返回一个元组，元组中包含了一个CreateTargetInfo对象，
    # 该对象描述了创建目标的相关信息，包括应用程序名称和类名。
    targets = (CreateTargetInfo("src.Ui.BotListPage.BotListWidget", "BotListWidget"),)

    # 静态方法available()，用于检查模块"BotListWidget"是否存在，返回值为布尔型。
    @staticmethod
    def available() -> bool:
        return exists_module("src.Ui.BotListPage.BotListWidget")

    # 静态方法create()，用于创建BotListWidget类的实例，返回值为BotListWidget对象。
    @staticmethod
    def create(create_type: [BotListWidget]) -> BotListWidget:
        return BotListWidget()


add_creator(BotListWidgetClassCreator)
