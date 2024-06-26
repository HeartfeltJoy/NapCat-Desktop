# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QUrl, QUrlQuery, Qt, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtNetwork import QNetworkRequest, QNetworkReply
from PySide6.QtWidgets import QVBoxLayout
from creart import it
from qfluentwidgets import CardWidget, ImageLabel, BodyLabel, setFont, ToolTipFilter

from src.Core.Config.ConfigModel import Config
from src.Core.NetworkFunc import Urls, NetworkFunc

if TYPE_CHECKING:
    from src.Ui.BotListPage.BotList import BotList
    from src.Ui.BotListPage.BotWidget import BotWidget


class BotCard(CardWidget):
    """
    ## 机器人卡片
    用于 BotList 内部展示的卡片

    ### 参数
        - config 传入的机器人配置
    """

    def __init__(self, config: Config, parent: "BotList" = None) -> None:
        super().__init__(parent=parent)
        self.config = config
        self.botWidget: Optional[BotWidget] = None
        self._initWidget()
        self._QQAvatar()
        self._infoLabel()
        self._setLayout()

    def _initWidget(self) -> None:
        """
        ## 初始化卡片并设置自身的一些参数
        """
        self.setFixedSize(190, 230)
        self.vBoxLayout = QVBoxLayout(self)

        self.clicked.connect(self._clickSlot)

    def _setLayout(self) -> None:
        """
        ## 布局卡片控件
        """
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addWidget(
            self.QQAvatarLabel, alignment=Qt.AlignmentFlag.AlignCenter,
        )
        self.vBoxLayout.addSpacing(25)
        self.vBoxLayout.addWidget(
            self.idLabel, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.vBoxLayout)

    def _infoLabel(self) -> None:
        """
        ## 卡片展示的一些 Label
        """
        self.idLabel = BodyLabel(f"{self.config.bot.name}", self)
        self.idLabel.setToolTip(self.idLabel.text())
        self.idLabel.setToolTipDuration(1000)
        self.idLabel.installEventFilter(ToolTipFilter(self.idLabel))
        setFont(self.idLabel, 16)

    def _QQAvatar(self) -> None:
        """
        ## 创建展示 QQ头像 的 ImageLabel
        """
        self.QQAvatarLabel = ImageLabel(":Global/logo.png", self)
        self.QQAvatarLabel.scaledToHeight(115)
        self.QQAvatarLabel.setBorderRadius(5, 5, 5, 5)

        # 处理 QQ头像 的 Url
        avatar_url: QUrl = Urls.QQ_AVATAR.value
        query = QUrlQuery()
        query.addQueryItem("spec", "640")
        query.addQueryItem("dst_uin", self.config.bot.QQID)
        avatar_url.setQuery(query)

        # 创建请求并链接槽函数
        request = QNetworkRequest(avatar_url)
        replay = it(NetworkFunc).manager.get(request)
        replay.finished.connect(lambda: self._setAvatar(replay))

    def _setAvatar(self, replay: QNetworkReply) -> None:
        """
        ## 设置头像
        """
        if replay.error() == QNetworkReply.NetworkError.NoError:
            # 如果请求成功则设置反之显示错误提示
            avatar = QPixmap()
            avatar.loadFromData(replay.readAll())
            self.QQAvatarLabel.setImage(avatar)
            self.QQAvatarLabel.scaledToHeight(115)
            self.QQAvatarLabel.setBorderRadius(5, 5, 5, 5)
        else:
            from src.Ui.BotListPage import BotListWidget
            it(BotListWidget).showError(
                title=self.tr("Failed to get the QQ avatar"),
                content=replay.errorString()
            )

    @Slot()
    def _clickSlot(self) -> None:
        """
        当自身被点击时
        """
        from src.Ui.BotListPage.BotListWidget import BotListWidget
        from src.Ui.BotListPage.BotWidget import BotWidget
        it(BotListWidget).topCard.addItem(f"{self.config.bot.name} ({self.config.bot.QQID})")
        it(BotListWidget).topCard.updateListButton.hide()

        if self.botWidget is None:
            self.botWidget = BotWidget(self.config)
            it(BotListWidget).view.addWidget(self.botWidget)
            it(BotListWidget).view.setCurrentWidget(self.botWidget)
        else:
            it(BotListWidget).view.setCurrentWidget(self.botWidget)
