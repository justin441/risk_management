import rules


@rules.predicate
def is_gm(user, business_unit):
    return business_unit.bu_manager == user


# rules
rules.add_rule('add_process_to_bu', is_gm)

# permissions
rules.add_perm('users.add_process_to_bu', is_gm)
rules.add_perm('users.add_businessunit', is_gm)




