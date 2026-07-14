from ..models.supabase_db import (
    get_active_profiles,
    get_alternative_scores,
    get_all_alternatives,
    get_cached_ranking,
    clear_department_rankings,
    save_department_ranking
)

def gap_to_score(gap):
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
    else:
        return 0

def calculate_alternative_score(alternative_id, department_id, core_weight=0.6):
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
            continue

        actual = scores[criteria_id]
        gap = actual - target
        score = gap_to_score(gap)

        if factor_type == 'core':
            core_scores.append(score * weight)
            total_weight_core += weight
        else:
            secondary_scores.append(score * weight)
            total_weight_secondary += weight

    ncf = sum(core_scores) / total_weight_core if total_weight_core > 0 else 0
    nsf = sum(secondary_scores) / total_weight_secondary if total_weight_secondary > 0 else 0
    total = (core_weight * ncf) + ((1 - core_weight) * nsf)

    return {
        'ncf': ncf,
        'nsf': nsf,
        'total': total
    }

def rank_alternatives(department_id, core_weight=0.6):
    """Ambil peringkat dari cache jika tersedia, jika tidak hitung & cache."""
    cached = get_cached_ranking(department_id)
    if cached:
        return [{
            'id': r['alternative_id'],
            'name': r['alternative_name'],
            'ncf': r['ncf'],
            'nsf': r['nsf'],
            'total': r['total']
        } for r in cached]

    # Hitung ulang
    alts = get_all_alternatives()
    results = []
    for alt in alts:
        res = calculate_alternative_score(alt['id'], department_id, core_weight)
        if res:
            results.append({
                'alternative_id': alt['id'],
                'name': alt['name'],
                'ncf': res['ncf'],
                'nsf': res['nsf'],
                'total': res['total']
            })
    results.sort(key=lambda x: x['total'], reverse=True)

    # Simpan ke cache (hapus dulu sebelumnya)
    clear_department_rankings(department_id)
    save_department_ranking(department_id, results)

    # Kembalikan format yang konsisten
    return [{
        'id': r['alternative_id'],
        'name': r['name'],
        'ncf': r['ncf'],
        'nsf': r['nsf'],
        'total': r['total']
    } for r in results]