from ..models.supabase_db import (
    get_active_profiles,
    get_alternative_scores,
    get_all_alternatives,
    get_cached_ranking,
    clear_department_rankings,
    save_department_ranking,
    get_all_aspects
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
    elif gap > 4:
        return 0.5
    else:
        return 0


def calculate_alternative_score(alternative_id, department_id, core_weight=0.6):
    """
    Hitung skor alternatif berdasarkan metode Profile Matching dengan Aspek.
    
    Algoritma:
    1. Ambil semua aspek yang aktif
    2. Untuk setiap aspek, kumpulkan kriteria core & secondary yang terikat pada aspek tersebut
    3. Rata-ratakan skor sub-kriteria per faktor (core → NCF, secondary → NSF) tanpa bobot kriteria,
       lalu gabungkan menjadi Nilai Aspek dengan porsi core_weight (default 0.6) / (1 - core_weight)
    4. Kalikan setiap Nilai Aspek dengan bobot aspeknya
    5. Jumlahkan untuk mendapatkan Ranking Final
    """
    try:
        profiles = get_active_profiles(department_id)
        if not profiles:
            return None

        scores = get_alternative_scores(alternative_id)

        aspects = get_all_aspects()
        aspect_map = {a['id']: a for a in aspects}
    except Exception:
        return None

    # Kelompokkan profiles berdasarkan aspect_id
    profiles_by_aspect = {}
    for profile in profiles:
        aid = profile.get('aspect_id')
        if aid not in profiles_by_aspect:
            profiles_by_aspect[aid] = []
        profiles_by_aspect[aid].append(profile)

    aspect_scores = []

    for aspect_id, profile_list in profiles_by_aspect.items():
        # Bobot untuk aspek ini
        if aspect_id is not None and aspect_id in aspect_map:
            aspect_weight = aspect_map[aspect_id]['weight']
        else:
            aspect_weight = 1.0

        core_scores = []
        secondary_scores = []

        for profile in profile_list:
            criteria_id = profile['criteria_id']
            target = profile['target_value']
            factor_type = profile['type']

            if criteria_id not in scores:
                continue

            actual = scores[criteria_id]
            gap = actual - target
            score = gap_to_score(gap)

            # Bobot kriteria tidak lagi dipakai; semua sub-kriteria dalam satu
            # faktor diperlakukan setara di dalam rata-rata (NCF/NSF).
            if factor_type == 'core':
                core_scores.append(score)
            else:
                secondary_scores.append(score)

        # Hitung NCF dan NSF untuk aspek ini (rata-rata biasa, tanpa bobot kriteria)
        ncf = sum(core_scores) / len(core_scores) if core_scores else 0
        nsf = sum(secondary_scores) / len(secondary_scores) if secondary_scores else 0

        # Nilai aspek = gabungan core & secondary
        nilai_aspek = (core_weight * ncf) + ((1 - core_weight) * nsf)

        aspect_scores.append({
            'aspect_id': aspect_id,
            'aspect_weight': aspect_weight,
            'nilai_aspek': nilai_aspek,
            'ncf': ncf,
            'nsf': nsf
        })

    if not aspect_scores:
        return None

    # Ranking final: total tertimbang dari semua nilai aspek
    total_tertimbang = sum(a['nilai_aspek'] * a['aspect_weight'] for a in aspect_scores)
    total_bobot = sum(a['aspect_weight'] for a in aspect_scores)
    total = total_tertimbang / total_bobot if total_bobot > 0 else 0

    return {
        'total': total,
        'aspect_scores': aspect_scores
    }


def rank_alternatives(department_id, core_weight=0.6):
    """Ambil peringkat dari cache jika tersedia, jika tidak hitung & cache."""
    try:
        cached = get_cached_ranking(department_id)
        if cached:
            return [{
                'id': r['alternative_id'],
                'name': r['alternative_name'],
                'total': r['total']
            } for r in cached]

        # Hitung ulang
        alts = get_all_alternatives()
        results = []
        for alt in alts:
            try:
                res = calculate_alternative_score(alt['id'], department_id, core_weight)
                if res:
                    results.append({
                        'alternative_id': alt['id'],
                        'name': alt['name'],
                        'total': res['total'],
                        'aspect_scores': res['aspect_scores']
                    })
            except Exception:
                continue
        results.sort(key=lambda x: x['total'], reverse=True)

        # Simpan ke cache (hapus dulu sebelumnya)
        clear_department_rankings(department_id)
        save_department_ranking(department_id, results)

        # Kembalikan format yang konsisten
        return [{
            'id': r['alternative_id'],
            'name': r['name'],
            'total': r['total']
        } for r in results]
    except Exception:
        return []
