"""Stage 9 conformance. Public Skill/API only; both stores."""

from memory_infra.skill import SkillApi

from tests.skill_conformance import assert_conformance


def test_stage9_memory_conformance():
    assert_conformance(SkillApi.open_memory)


def test_stage9_file_conformance(tmp_path):
    path = tmp_path / "stage9.json"

    def open_file():
        return SkillApi.open_file(path)

    assert_conformance(open_file)
