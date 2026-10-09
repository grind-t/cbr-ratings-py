from cbr_ratings._core.kra import convert_kra_name


def test_converts_kra_name(subtests):
    cases = {
        'АО "Эксперт РА"': "EXPERT_RA",
        "АКРА (АО)": "AKRA",
        'ООО "НКР"': "NKR",
        'ООО "НРА"': "NRA",
        "Unknown": "UNKNOWN",
    }
    for value, expected in cases.items():
        with subtests.test(value=value):
            assert convert_kra_name(value) == expected
