class GptunnelRequiredPaymentException(RuntimeError):
    def __init__(self):
        super().__init__("💵 Языковая модель не смогла обработать запрос, так как на аккаунте сервиса GPTunnel закончились средства. Пополните средства для продолжения работы API.")

