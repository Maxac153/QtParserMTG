class MtgPricesError(Exception):
    """Базовая ошибка приложения. Текст сообщения показывается пользователю."""


class InvalidLinkError(MtgPricesError):
    pass


class FetchError(MtgPricesError):
    pass


class ParseError(MtgPricesError):
    pass


class DuplicateCardError(MtgPricesError):
    pass


class CardNotFoundError(MtgPricesError):
    pass


class ImportFileError(MtgPricesError):
    pass
