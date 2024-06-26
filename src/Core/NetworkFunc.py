# -*- coding: utf-8 -*-
import json
from abc import ABC
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Optional, IO, Callable, Any
from loguru import logger

from PySide6.QtCore import QUrl, QEventLoop, QRegularExpression, Signal, Slot, QObject
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from creart import exists_module, AbstractCreator, CreateTargetInfo, add_creator, it


class Urls(Enum):
    """
    ## 软件内部可能用的到的 Url
    """
    # NCD相关地址
    NCD_REPO = QUrl("https://github.com/HeartfeltJoy/NapCatQQ-Desktop")
    NCD_ISSUES = QUrl("https://github.com/HeartfeltJoy/NapCatQQ-Desktop/issues")

    # NapCat 相关地址
    NAPCATQQ_REPO = QUrl("https://github.com/NapNeko/NapCatQQ")
    NAPCATQQ_ISSUES = QUrl("https://github.com/NapNeko/NapCatQQ/issues")
    NAPCATQQ_REPO_API = QUrl("https://api.github.com/repos/NapNeko/NapCatQQ/releases/latest")
    NAPCATQQ_DOCUMENT = QUrl("https://napneko.github.io/")

    # 直接写入下载地址, 不请求 API 获取, 期望达到节省时间的目的
    NAPCAT_ARM64_LINUX = QUrl("https://github.com/NapNeko/NapCatQQ/releases/latest/download/NapCat.linux.arm64.zip")
    NAPCAT_64_LINUX = QUrl("https://github.com/NapNeko/NapCatQQ/releases/latest/download/NapCat.linux.x64.zip")
    NAPCAT_WIN = QUrl("https://github.com/NapNeko/NapCatQQ/releases/latest/download/NapCat.win32.x64.zip")

    # QQ 相关
    QQ_OFFICIAL_WEBSITE = QUrl("https://im.qq.com/index/")
    QQ_WIN_DOWNLOAD = QUrl("https://cdn-go.cn/qq-web/im.qq.com_new/latest/rainbow/windowsDownloadUrl.js")
    QQ_AVATAR = QUrl("https://q.qlogo.cn/headimg_dl")


class NetworkFunc(QObject):
    """
    ## 软件内部的所有网络请求均通过此类实现
    """
    response_ready = Signal(QNetworkReply)

    def __init__(self):
        """
        ## 创建 QNetworkAccessManager
        """
        super().__init__()
        self.manager = QNetworkAccessManager()


class NetworkFuncClassCreator(AbstractCreator, ABC):
    # 定义类方法targets，该方法返回一个元组，元组中包含了一个CreateTargetInfo对象，
    # 该对象描述了创建目标的相关信息，包括应用程序名称和类名。
    targets = (CreateTargetInfo("src.Core.NetworkFunc", "NetworkFunc"),)

    # 静态方法available()，用于检查模块"PathFunc"是否存在，返回值为布尔型。
    @staticmethod
    def available() -> bool:
        return exists_module("src.Core.NetworkFunc")

    # 静态方法create()，用于创建PathFunc类的实例，返回值为PathFunc对象。
    @staticmethod
    def create(create_type: [NetworkFunc]) -> NetworkFunc:
        return NetworkFunc()


add_creator(NetworkFuncClassCreator)


def async_request(url: QUrl) -> Callable[[Callable[..., None]], Callable[..., None]]:
    """
    装饰器函数，用于装饰其他函数，使其在QUrl请求完成后执行
        - url (QUrl): 用于进行网络请求的QUrl对象。
    """
    def decorator(func: Callable[..., None]) -> Callable[..., None]:
        """
        装饰器内部函数，用于接收被装饰的函数
            - func (Callable): 被装饰的函数
        """
        def wrapper(*args: Any, **kwargs: Any) -> None:
            """
            包装函数，用于执行网络请求并在请求完成后调用被装饰的函数。
                - *args: 传递给被装饰函数的位置参数
                - **kwargs: 传递给被装饰函数的关键字参数
            """
            def on_finished(_reply: QNetworkReply) -> None:
                """
                请求完成后的回调函数，读取响应并调用被装饰的函数。
                    - reply (QNetworkReply): 网络响应对象
                """
                if _reply.error() == QNetworkReply.NetworkError.NoError:
                    # 调用被装饰的函数并传递响应数据
                    func(*args, reply=_reply.readAll().data().decode().strip(), *kwargs)
                else:
                    func(*args, reply=None, *kwargs)
                    logger.error(f"Error: {_reply.errorString()}")
                # 清理回复对象
                _reply.deleteLater()

            # 创建并发送网络请求
            request = QNetworkRequest(url)
            reply = it(NetworkFunc).manager.get(request)
            # 连接请求完成信号到回调函数
            reply.finished.connect(lambda: on_finished(reply))

        return wrapper
    return decorator


class Downloader(QObject):
    """
    ## 执行下载任务
    """
    downloadProgress = Signal(int)
    finished = Signal(bool)
    errorOccurred = Signal(str, str)

    def __init__(self, url: QUrl = None, path: Path = None):
        """
        ## 初始化下载器
            - url 下载连接
            - path 下载路径
        """
        super().__init__()
        self.url: QUrl = url if url else None
        self.path: Path = path if path else None

        self.request = QNetworkRequest(self.url) if self.url else QNetworkRequest()
        self.reply: Optional[QNetworkReply] = None
        self.file: Optional[IO[bytes]] = None

    def setUrl(self, url: QUrl):
        self.url = url
        self.request.setUrl(self.url)

    def setPath(self, path: Path):
        self.path = path

    def start(self):
        """
        ## 启动下载
        """
        # 打开文件以写入下载数据
        self.file = open(str(self.path / self.url.fileName()), 'wb')
        # 执行下载任务并连接信号
        self.reply = it(NetworkFunc).manager.get(self.request)
        self.reply.downloadProgress.connect(self._downloadProgressSlot)
        self.reply.readyRead.connect(self._read2File)
        self.reply.finished.connect(self._finished)
        self.reply.errorOccurred.connect(self._error)

    def stop(self):
        """
        ## 停止下载
        """
        self.reply.abort() if self.reply else None

    @Slot()
    def _downloadProgressSlot(self, bytes_received: int, bytes_total: int):
        """
        ## 下载进度槽函数
            - bytes_received 接收的字节数
            - bytes_total 总字节数
        """
        if bytes_total > 0:
            # 防止发生零除以零的情况
            self.downloadProgress.emit(int((bytes_received / bytes_total) * 100))

    @Slot()
    def _read2File(self):
        """
        ## 读取数据并写入文件
        """
        if self.file:
            self.file.write(self.reply.readAll())

    @Slot()
    def _finished(self):
        """
        ## 下载结束并发送信号
        """
        if self.file:
            # 防止文件中途丢失导致关闭一个没有打开的文件引发报错
            self.file.close()
            self.file = None
        if self.reply.error() != QNetworkReply.NetworkError.NoError:
            self.finished.emit(False)
            return

        self.finished.emit(True)

    @Slot()
    def _error(self, error_code):
        if self.file:
            self.file.close()
            self.file = None
        self.finished.emit(False)
        self.errorOccurred.emit(self.reply.errorString(), str(error_code))
