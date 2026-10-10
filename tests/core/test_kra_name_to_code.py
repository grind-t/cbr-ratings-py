from cbr_ratings._core.rating.kra import kra_name_to_code


def test_converts_kra_name_to_code(subtests):
    cases = {
        'АО "Эксперт РА"': "EXPERT_RA",
        "АКРА (АО)": "AKRA",
        'ООО "НКР"': "NKR",
        'ООО "НРА"': "NRA",
    }
    for value, expected in cases.items():
        with subtests.test(value=value):
            assert kra_name_to_code(value) == expected
