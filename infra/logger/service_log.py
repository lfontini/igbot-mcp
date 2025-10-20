import logging
import sys
from typing import Optional


class Logger:
    """
    Classe centralizada para configuração de logs no projeto.
    """

    _logger: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls, name: str = "app", level: int = logging.INFO) -> logging.Logger:
        """
        Retorna um logger configurado com o schema padronizado.
        """
        if cls._logger is None:
            # Cria instância do logger
            logger = logging.getLogger(name)
            logger.setLevel(level)

            # Evita duplicação de handlers
            if not logger.handlers:
                handler = logging.StreamHandler(sys.stdout)

                # Definindo schema sofisticado de logs
                formatter = logging.Formatter(
                    fmt=(
                        "%(asctime)s | "
                        "%(levelname)-8s | "
                        "%(name)s | "
                        "module=%(module)s | "
                        "func=%(funcName)s | "
                        "line=%(lineno)d | "
                        "message=%(message)s"
                    ),
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)

            cls._logger = logger

        return cls._logger
