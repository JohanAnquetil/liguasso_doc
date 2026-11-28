"""L'adaptateur ALTCHA avec de vraies preuves de travail (difficulté réduite)."""
import altcha
import pytest

from liguasso_contrib.domaine.erreurs import Invalide
from liguasso_contrib.infrastructure.anti_robot import AntiRobotAltcha
from liguasso_contrib.infrastructure.sqlite import Base, DefisUtilisesSQLite


@pytest.fixture
def anti_robot(tmp_path):
    return AntiRobotAltcha("secret-de-test", 10, DefisUtilisesSQLite(Base(tmp_path / "a.sqlite3")))


def resoudre(defi: dict) -> str:
    d = altcha.Challenge.from_dict(defi)
    return altcha.Payload(d, altcha.solve_challenge(d)).to_base64()


def test_preuve_valide_une_seule_fois(anti_robot):
    preuve = resoudre(anti_robot.creer_defi())
    anti_robot.verifier(preuve)
    with pytest.raises(Invalide, match="déjà utilisée"):
        anti_robot.verifier(preuve)


@pytest.mark.parametrize("preuve", ["", "pas-du-base64", "eyJ9"])
def test_preuves_invalides(anti_robot, preuve):
    with pytest.raises(Invalide):
        anti_robot.verifier(preuve)


def test_defi_d_un_autre_serveur_refuse(anti_robot, tmp_path):
    autre = AntiRobotAltcha("autre-secret", 10, DefisUtilisesSQLite(Base(tmp_path / "b.sqlite3")))
    with pytest.raises(Invalide):
        anti_robot.verifier(resoudre(autre.creer_defi()))
