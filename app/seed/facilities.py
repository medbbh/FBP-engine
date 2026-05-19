from decimal import Decimal

FACILITIES = [
    # Nouakchott — urban hospitals (equity 1.0)
    {"name": "Hôpital National de Nouakchott", "type": "CHN", "region": "Nouakchott", "district": "Tevragh-Zeina", "is_rural": False, "equity_coefficient": Decimal("1.0")},
    {"name": "Centre de Santé Ksar", "type": "Centre Santé", "region": "Nouakchott", "district": "Ksar", "is_rural": False, "equity_coefficient": Decimal("1.0")},
    {"name": "CSB Toujounine", "type": "CSB", "region": "Nouakchott", "district": "Toujounine", "is_rural": False, "equity_coefficient": Decimal("1.0")},
    {"name": "Centre de Santé Arafat", "type": "Centre Santé", "region": "Nouakchott", "district": "Arafat", "is_rural": False, "equity_coefficient": Decimal("1.0")},

    # Trarza — semi-rural (equity 1.2)
    {"name": "Hôpital Régional de Rosso", "type": "Hôpital District", "region": "Trarza", "district": "Rosso", "is_rural": False, "equity_coefficient": Decimal("1.2")},
    {"name": "CSB Boutilimit", "type": "CSB", "region": "Trarza", "district": "Boutilimit", "is_rural": True, "equity_coefficient": Decimal("1.3")},
    {"name": "CSB R'Kiz", "type": "CSB", "region": "Trarza", "district": "R'Kiz", "is_rural": True, "equity_coefficient": Decimal("1.3")},

    # Brakna — semi-rural
    {"name": "Hôpital Régional d'Aleg", "type": "Hôpital District", "region": "Brakna", "district": "Aleg", "is_rural": False, "equity_coefficient": Decimal("1.2")},
    {"name": "CSB Magta-Lahjar", "type": "CSB", "region": "Brakna", "district": "Magta-Lahjar", "is_rural": True, "equity_coefficient": Decimal("1.3")},

    # Adrar — remote/desert (equity 1.4-1.5)
    {"name": "Hôpital Régional d'Atar", "type": "CHR", "region": "Adrar", "district": "Atar", "is_rural": False, "equity_coefficient": Decimal("1.3")},
    {"name": "CSB Aoujeft", "type": "CSB", "region": "Adrar", "district": "Aoujeft", "is_rural": True, "equity_coefficient": Decimal("1.5")},
    {"name": "CSB Chinguetti", "type": "CSB", "region": "Adrar", "district": "Chinguetti", "is_rural": True, "equity_coefficient": Decimal("1.5")},

    # Hodh El Gharbi
    {"name": "Hôpital Régional d'Aioun", "type": "Hôpital District", "region": "Hodh El Gharbi", "district": "Aioun", "is_rural": False, "equity_coefficient": Decimal("1.2")},
    {"name": "CSB Tintane", "type": "CSB", "region": "Hodh El Gharbi", "district": "Tintane", "is_rural": True, "equity_coefficient": Decimal("1.4")},

    # Gorgol
    {"name": "Hôpital Régional de Kaédi", "type": "Hôpital District", "region": "Gorgol", "district": "Kaédi", "is_rural": False, "equity_coefficient": Decimal("1.2")},
    {"name": "CSB Maghama", "type": "CSB", "region": "Gorgol", "district": "Maghama", "is_rural": True, "equity_coefficient": Decimal("1.3")},

    # Assaba
    {"name": "Hôpital Régional de Kiffa", "type": "CHR", "region": "Assaba", "district": "Kiffa", "is_rural": False, "equity_coefficient": Decimal("1.2")},

    # Tagant
    {"name": "Centre de Santé Tidjikja", "type": "Centre Santé", "region": "Tagant", "district": "Tidjikja", "is_rural": True, "equity_coefficient": Decimal("1.4")},

    # Dakhlet Nouadhibou
    {"name": "Hôpital de Nouadhibou", "type": "Hôpital District", "region": "Dakhlet Nouadhibou", "district": "Nouadhibou", "is_rural": False, "equity_coefficient": Decimal("1.1")},

    # Tiris Zemmour — very remote
    {"name": "CSB Zouerate", "type": "CSB", "region": "Tiris Zemmour", "district": "Zouerate", "is_rural": True, "equity_coefficient": Decimal("1.5")},
]
