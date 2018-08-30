import rules


# ------------predicates------------

# Processus
@rules.predicate
def is_process_manager(user, processus):
    return processus.proc_manager == user


@rules.predicate
def is_process_upper_mgt(user, processus):
    bu = processus.business_unit
    return bu.bu_manager == user


# Activités
@rules.predicate
def is_activity_owner(user, activite):
    return activite.responsable == user


@rules.predicate
def is_activity_supervisor(user, activite):
    processus = activite.processus
    return processus.proc_manager == user


@rules.predicate
def is_activity_upper_mgt(user, activite):
    processus = activite.processus
    bu = processus.business_unit
    return bu.bu_manager == user


# Risques des activités
@rules.predicate
def is_activity_risk_reporter(user, activiterisque):
    return activiterisque.soumis_par == user


@rules.predicate
def is_activity_risk_owner(user, activiterisque):
    return activiterisque.proprietaire == user


@rules.predicate
def is_activity_risk_monitor(user, activiterisque):
    activite = activiterisque.activite
    return activite.responsable == user


@rules.predicate
def is_activity_risk_supervisor(user, activiterisque):
    processus = activiterisque.activite.processus
    return processus.proc_manager == user


@rules.predicate
def is_activity_risk_upper_mgt(user, activiterisque):
    processus = activiterisque.activite.processus
    bu = processus.business_unit
    return bu.bu_manager == user


# Risques des processus
@rules.predicate
def is_process_risk_reporter(user, processusrisque):
    if processusrisque.soumis_par:
        return processusrisque.soumis_par == user
    return False


@rules.predicate
def is_process_risk_owner(user, processusrisque):
    return processusrisque.proprietaire == user


@rules.predicate
def is_process_risk_monitor(user, processusrisque):
    processus = processusrisque.processus
    return processus.proc_manager == user


@rules.predicate
def is_process_risk_upper_mgt(user, processusrisque):
    bu = processusrisque.processus.business_unit
    return bu.bu_manager == user


# Estimations
@rules.predicate
def is_estimation_monitor(user, estimation):
    try:
        return estimation.content_object.activite.processus.proc_manager == user
    except AttributeError:
        return estimation.content_object.processus.proc_manager == user


# Contrôles
@rules.predicate
def is_controle_creator(user, controle):
    return controle.cree_par == user


@rules.predicate
def is_controle_owner(user, controle):
    if controle.assigne_a:
        return controle.assigne_a == user
    return False


@rules.predicate
def is_controle_reviewer(user, controle):
    try:
        return controle.content_object.activite.processus.proc_manager == user
    except AttributeError:
        return controle.content_object.processus.proc_manager == user


# Risques
@rules.predicate
def is_risk_creator(user, risque):
    return risque.cree_par == user


# Identification Risques
@rules.predicate
def is_risk_verifier(user, identificationrisque):
    if identificationrisque.get_class == 'ProcessusRisque':
        return is_process_risk_monitor(user, identificationrisque) \
               or is_process_risk_upper_mgt(user, identificationrisque)
    elif identificationrisque.get_class == 'ActiviteRisque':
        return is_activity_risk_monitor(user, identificationrisque) \
               or is_activity_risk_supervisor(user, identificationrisque) \
               or is_activity_risk_upper_mgt(user, identificationrisque)


# ------------rules------------
# Risques
rules.add_rule('change_risque', is_risk_creator)

# Identification Risques
rules.add_rule('verify_risk', is_risk_verifier)

# Processus
rules.add_rule('change_processus', is_process_upper_mgt)
rules.add_rule('delete_processus', is_process_upper_mgt)
rules.add_rule('add_activity_to_process', is_process_manager | is_process_upper_mgt)
rules.add_rule('add_process_data', is_process_manager | is_process_upper_mgt)
rules.add_rule('add_process_risk', rules.is_authenticated)

# Activités
rules.add_rule('change_activite', is_activity_supervisor | is_activity_upper_mgt)
rules.add_rule('delete_activite', is_activity_supervisor | is_activity_upper_mgt)
rules.add_rule('add_activity_risk', rules.is_authenticated)
rules.add_rule('complete_activity', is_activity_owner | is_activity_supervisor)

# Risques des activités

rules.add_rule('set_seuil_activity_risk', is_activity_risk_supervisor | is_activity_risk_upper_mgt)
rules.add_rule('set_review_date_activity_risk', is_activity_risk_supervisor | is_activity_risk_upper_mgt)
rules.add_rule('add_control_activity_risk', is_activity_risk_reporter | is_activity_risk_monitor |
               is_activity_risk_owner | is_activity_risk_supervisor | is_activity_risk_upper_mgt)
rules.add_rule('assign_activity_risk', is_activity_risk_supervisor | is_activity_risk_upper_mgt)
rules.add_rule('estimate_activity_risk', is_activity_risk_supervisor | is_activity_risk_upper_mgt)
rules.add_rule('change_activiterisque', is_activity_risk_supervisor |
               is_activity_risk_upper_mgt | is_activity_risk_reporter)
rules.add_rule('delete_activiterisque', is_activity_risk_supervisor | is_activity_risk_upper_mgt)

# Risques des processus
rules.add_rule('set_seuil_process_risk', is_process_risk_monitor | is_process_risk_upper_mgt)
rules.add_rule('set_review_date_process_risk', is_process_risk_upper_mgt | is_process_risk_monitor)
rules.add_rule('add_control_process_risk', is_process_risk_owner | is_process_risk_monitor | is_process_risk_upper_mgt
               | is_activity_risk_reporter)
rules.add_rule('assign_process_risk', is_process_risk_monitor | is_process_risk_upper_mgt)
rules.add_rule('estimate_process_risk', is_process_risk_upper_mgt | is_process_risk_monitor)
rules.add_rule('change_processusrisque', is_process_risk_upper_mgt |
               is_process_risk_monitor | is_process_risk_reporter)
rules.add_rule('delete_processusrisque', is_process_risk_monitor | is_process_risk_upper_mgt)

# Estimations
rules.add_rule('set_estimation_review_date', is_estimation_monitor)

# Contrôles
rules.add_rule('assign_control', is_controle_reviewer)
rules.add_rule('complete_control', is_controle_owner)
rules.add_rule('change_controle', is_controle_reviewer | is_controle_creator)
rules.add_rule('delete_controle', is_controle_creator | is_controle_reviewer)
rules.add_rule('approve_controle', is_controle_reviewer)
rules.add_rule('validate_controle_completion', is_controle_reviewer | is_controle_creator)

# ------------permissions------------
# Risques
rules.add_perm('risk_register.change_risque', is_risk_creator)

# Identification Risques
rules.add_perm('risk_register.verify_risque', is_risk_verifier)

# Processus
rules.add_perm('risk_register.change_processus', is_process_upper_mgt)
rules.add_perm('risk_register.delete_processus', is_process_upper_mgt)
rules.add_perm('risk_register.add_activity_to_process', is_process_manager | is_process_upper_mgt)
rules.add_perm('risk_register.add_process_data', is_process_manager | is_process_upper_mgt)
rules.add_perm('risk_register.add_process_risk', rules.is_authenticated)

# Activités
rules.add_perm('risk_register.change_activite', is_activity_supervisor | is_activity_upper_mgt)
rules.add_perm('risk_register.delete_activite', is_activity_supervisor | is_activity_upper_mgt)
rules.add_perm('risk_register.add_activity_risk', rules.is_authenticated)
rules.add_perm('risk_register_complete_activity', is_activity_owner | is_activity_supervisor | is_activity_upper_mgt)

# Risques des activités

rules.add_perm('risk_register.set_seuil_activity_risk', is_activity_risk_supervisor | is_activity_risk_upper_mgt)
rules.add_perm('risk_register.set_review_date_activity_risk', is_activity_risk_supervisor | is_activity_risk_upper_mgt)
rules.add_perm('risk_register.add_control_activity_risk', is_activity_risk_reporter | is_activity_risk_monitor |
               is_activity_risk_owner | is_activity_risk_supervisor | is_activity_risk_upper_mgt)
rules.add_perm('risk_register.assign_activity_risk', is_activity_risk_supervisor | is_activity_risk_upper_mgt)
rules.add_perm('risk_register.estimate_activity_risk',
               is_activity_risk_supervisor | is_activity_risk_upper_mgt | is_activity_risk_reporter)
rules.add_perm('risk_register.change_activiterisque', is_activity_risk_supervisor |
               is_activity_risk_upper_mgt | is_activity_risk_reporter)
rules.add_perm('risk_register.delete_activiterisque', is_activity_risk_supervisor | is_activity_risk_upper_mgt)

# Risques des processus
rules.add_perm('risk_register.set_seuil_process_risk', is_process_risk_monitor | is_process_risk_upper_mgt)
rules.add_perm('risk_register.set_review_date_process_risk', is_process_risk_upper_mgt | is_process_risk_monitor)
rules.add_perm('risk_register.add_control_process_risk', is_process_risk_owner | is_process_risk_monitor |
               is_process_risk_upper_mgt | is_process_risk_reporter)
rules.add_perm('risk_register.assign_process_risk', is_process_risk_monitor | is_process_risk_upper_mgt)
rules.add_perm('risk_register.estimate_process_risk', is_process_risk_upper_mgt | is_process_risk_monitor |
               is_process_risk_owner | is_process_risk_reporter)
rules.add_perm('risk_register.change_processusrisque', is_process_risk_upper_mgt |
               is_process_risk_monitor | is_process_risk_reporter)
rules.add_perm('risk_register.delete_processusrisque', is_process_risk_monitor | is_process_risk_upper_mgt)

# Estimations
rules.add_perm('risk_register.set_estimation_review_date', is_estimation_monitor)

# Contrôles
rules.add_perm('risk_register.assign_control', is_controle_reviewer)
rules.add_perm('risk_register.complete_control', is_controle_owner)
rules.add_perm('risk_register.change_controle', is_controle_reviewer | is_controle_creator)
rules.add_perm('risk_register.delete_controle', is_controle_creator | is_controle_reviewer)
rules.add_perm('risk_register.approve_controle', is_controle_reviewer)
rules.add_perm('risk_register.validate_controle_completion', is_controle_reviewer | is_controle_creator)
