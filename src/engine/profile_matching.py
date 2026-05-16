from ..models.data_structure import get_active_profiles, get_alternative_scores

def gap_to_score(gap):
    """Konversi nilai GAP ke skor Profile Matching."""
    if gap == 0:
        return 5
    elif gap == 1:
        return 4.5
    elif gap == -1:
        return 4
    elif gap == 2:
        return 3.5
    elif gap == -2:
        return 3
    elif gap == 3:
        return 2.5
    elif gap == -3:
        return 2
    elif gap == 4:
        return 1.5
    elif gap == -4:
        return 1
    elif gap > 4:
        return 0.5
    else:  # < -4
        return 0

def calculate_alternative_score(alternative_id, department_id, core_weight=0.6):
    """
    Menghitung total skor satu alternatif untuk suatu departemen.
    Mengembalikan dict: { 'ncf', 'nsf', 'total' }
    """
    profiles = get_active_profiles(department_id)
    if not profiles:
        return None

    scores = get_alternative_scores(alternative_id)
    
    core_scores = []
    secondary_scores = []
    total_weight_core = 0.0
    total_weight_secondary = 0.0

    for profile in profiles:
        criteria_id = profile['criteria_id']
        target = profile['target_value']
        weight = profile['weight']
        factor_type = profile['type']

        if criteria_id not in scores:
            continue  # kriteria tidak dinilai, lewati

        actual = scores[criteria_id]
        gap = actual - target
        score = gap_to_score(gap)

        if factor_type == 'core':
            core_scores.append(score * weight)
            total_weight_core += weight
        else:
            secondary_scores.append(score * weight)
            total_weight_secondary += weight

    # Hitung rata-rata tertimbang
    ncf = sum(core_scores) / total_weight_core if total_weight_core > 0 else 0
    nsf = sum(secondary_scores) / total_weight_secondary if total_weight_secondary > 0 else 0

    total = (core_weight * ncf) + ((1 - core_weight) * nsf)
    return {
        'ncf': ncf,
        'nsf': nsf,
        'total': total
    }

def rank_alternatives(department_id, core_weight=0.6):
    """Menghitung dan mengurutkan semua alternatif di satu departemen."""
    from ..models.data_structure import get_department_alternatives
    alts = get_department_alternatives(department_id)
    results = []
    for alt in alts:
        res = calculate_alternative_score(alt['id'], department_id, core_weight)
        if res:
            results.append({
                'id': alt['id'],
                'name': alt['name'],
                'ncf': res['ncf'],
                'nsf': res['nsf'],
                'total': res['total']
            })
    # Urutkan berdasarkan total menurun
    results.sort(key=lambda x: x['total'], reverse=True)
    return results