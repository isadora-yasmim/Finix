"""Garante que as migrations do Alembic formam uma cadeia única e íntegra.

Uma migration apontando para um ``down_revision`` inexistente só quebra na hora do
``alembic upgrade head`` — ou seja, no deploy. Este teste pega isso no CI.
"""

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

BACKEND_DIR = Path(__file__).resolve().parent.parent


def _script_directory() -> ScriptDirectory:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return ScriptDirectory.from_config(config)


def test_migrations_tem_um_unico_head() -> None:
    assert len(_script_directory().get_heads()) == 1


def test_migrations_encadeiam_do_head_ate_a_base() -> None:
    revisions = list(_script_directory().walk_revisions("base", "heads"))
    assert revisions, "nenhuma migration encontrada"
    assert revisions[-1].down_revision is None
