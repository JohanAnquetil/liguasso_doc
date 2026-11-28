"""Erreurs métier. L'interface HTTP les traduit en codes de réponse."""


class ErreurMetier(Exception):
    code = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class Invalide(ErreurMetier):
    code = 400


class NonAutorise(ErreurMetier):
    code = 401


class Introuvable(ErreurMetier):
    code = 404


class Conflit(ErreurMetier):
    code = 409


class TropDeDemandes(ErreurMetier):
    code = 429

    def __init__(self, message: str = "Trop de demandes. Réessayez dans quelques minutes."):
        super().__init__(message)


class ServiceExterne(ErreurMetier):
    code = 502


class Indisponible(ErreurMetier):
    code = 503
