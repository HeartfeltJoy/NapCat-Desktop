# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget
from creart import it
from qfluentwidgets import ExpandLayout, FluentIcon, ScrollArea

from src.Core.PathFunc import PathFunc
from src.Core.Config.ConfigModel import AdvancedConfig
from src.Ui.common.InputCard import (
    SwitchConfigCard,
    FolderConfigCard,
    ComboBoxConfigCard,
)

if TYPE_CHECKING:
    pass


class AdvancedWidget(ScrollArea):
    """
    ## Advance Item 项对应的 QWidget
    """

    def __init__(self, parent=None, config: AdvancedConfig = None) -> None:
        super().__init__(parent=parent)
        self.setObjectName("AdvanceWidget")
        self.view = QWidget()
        self.cardLayout = ExpandLayout(self.view)

        # 设置 ScrollArea
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setObjectName("AdvanceWidgetView")

        # 调用方法
        self._initWidget()
        self._setLayout()

        if config is not None:
            # 如果传入了 config 则进行解析并填充内部卡片
            self.config = config
            self.fillValue()

    def _initWidget(self) -> None:
        """
        ## 初始化 QWidget 所需要的控件并配置
        创建 InputCard
        """
        self.QQPathCard = FolderConfigCard(
            icon=FluentIcon.FOLDER,
            title=self.tr("Specify QQ path"),
            content=str(it(PathFunc).getQQPath()),
            parent=self.view,
        )
        self.startScriptPathCard = FolderConfigCard(
            icon=FluentIcon.FOLDER,
            title=self.tr("Specifies the path created by the script"),
            content=str(it(PathFunc).getStartScriptPath()),
            parent=self.view,
        )
        self.ffmpegPathCard = FolderConfigCard(
            icon=FluentIcon.MUSIC_FOLDER,
            title=self.tr("Specifies ffmpeg path"),
            parent=self.view,
        )
        self.debugModeCard = SwitchConfigCard(
            icon=FluentIcon.COMMAND_PROMPT,
            title=self.tr("Debug"),
            content=self.tr("The message will carry a raw field, " "which is the original message content"),
            parent=self.view,
        )
        self.localFile2UrlCard = SwitchConfigCard(
            icon=FluentIcon.SHARE,
            title=self.tr("LocalFile2Url"),
            content=self.tr(
                "If the URL cannot be obtained when calling the get file interface, "
                "use the base 64 field to return the file content"
            ),
            parent=self.view,
        )
        self.fileLogCard = SwitchConfigCard(
            icon=FluentIcon.SAVE_AS,
            title=self.tr("Whether to enable file logging"),
            content=self.tr("Log to a file(It is off by default)"),
            parent=self.view,
        )
        self.consoleLogCard = SwitchConfigCard(
            icon=FluentIcon.COMMAND_PROMPT,
            title=self.tr("Whether to enable console logging"),
            content=self.tr("Log to a console(It is off by default)"),
            parent=self.view,
        )
        self.fileLogLevelCard = ComboBoxConfigCard(
            icon=FluentIcon.EMOJI_TAB_SYMBOLS,
            title=self.tr("File log level"),
            content=self.tr("Set the log level when the output file is output (default debug)"),
            texts=["debug", "info", "error"],
            parent=self.view,
        )
        self.consoleLevelCard = ComboBoxConfigCard(
            icon=FluentIcon.EMOJI_TAB_SYMBOLS,
            title=self.tr("Console log level"),
            content=self.tr("Setting the Console Output Log Level (Default Info)"),
            texts=["info", "debug", "error"],
            parent=self.view,
        )

        self.cards = [
            self.QQPathCard,
            self.startScriptPathCard,
            self.ffmpegPathCard,
            self.debugModeCard,
            self.localFile2UrlCard,
            self.fileLogCard,
            self.consoleLogCard,
            self.fileLogLevelCard,
            self.consoleLevelCard,
        ]

    def fillValue(self) -> None:
        """
        ## 如果传入了 config 则对其内部卡片的值进行填充
        """
        self.QQPathCard.fillValue(self.config.QQPath)
        self.startScriptPathCard.fillValue(self.config.startScriptPath)
        self.ffmpegPathCard.fillValue(self.config.ffmpegPath)
        self.debugModeCard.fillValue(self.config.debug)
        self.localFile2UrlCard.fillValue(self.config.localFile2url)
        self.fileLogCard.fillValue(self.config.fileLog)
        self.consoleLogCard.fillValue(self.config.consoleLog)
        self.fileLogLevelCard.fillValue(self.config.fileLogLevel)
        self.consoleLevelCard.fillValue(self.config.consoleLogLevel)

    def _setLayout(self) -> None:
        """
        ## 将 QWidget 内部的 InputCard 添加到布局中
        """
        self.cardLayout.setContentsMargins(0, 0, 0, 0)
        self.cardLayout.setSpacing(2)
        for card in self.cards:
            self.cardLayout.addWidget(card)
            self.adjustSize()

        self.view.setLayout(self.cardLayout)

    def getValue(self) -> dict:
        """
        ## 返回内部卡片的配置结果
        """
        return {
            "QQPath": self.QQPathCard.getValue(),
            "startScriptPath": self.startScriptPathCard.getValue(),
            "ffmpegPath": self.ffmpegPathCard.getValue(),
            "debug": self.debugModeCard.getValue(),
            "localFile2url": self.localFile2UrlCard.getValue(),
            "fileLog": self.fileLogCard.getValue(),
            "consoleLog": self.consoleLogCard.getValue(),
            "fileLogLevel": self.fileLogLevelCard.getValue(),
            "consoleLogLevel": self.consoleLevelCard.getValue(),
        }

    def clearValues(self) -> None:
        """
        ## 清空(还原)内部卡片的配置
        """
        for card in self.cards:
            card.clear()

    def adjustSize(self) -> None:
        h = self.cardLayout.heightForWidth(self.width()) + 46
        return self.resize(self.width(), h)
