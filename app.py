import sys
import os

# Tambahkan root project ke path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import zipfile
from io import BytesIO
from flask import Flask, render_template, request, jsonify, send_file
from src.models.supabase_db import (
    create_tables,
    get_all_aspects, create_aspect, update_aspect, delete_aspect, get_aspect_by_id,
    get_all_criteria, create_criteria, update_criteria, delete_criteria, get_criteria_by_id,
    get_all_departments, create_department, update_department, delete_department, get_department_by_id,
    get_department_profiles, add_department_profile, update_department_profile, delete_department_profile,
    get_all_alternatives, create_alternative, update_alternative, delete_alternative, get_alternative_by_id,
    get_alternative_scores, set_alternative_score,
    clear_department_rankings, clear_all_rankings
)
from src.engine.profile_matching_web import rank_alternatives
from src.utils.io_utils import export_to_json, import_from_json, validate_import_data
from src.utils.pdf_export import export_rankings_to_pdf, export_report_without_rankings, export_all_data_to_pdf

app = Flask(__name__)

# ============================================================
# ROUTES: Halaman
# ============================================================

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/criteria')
def criteria_page():
    return render_template('criteria.html')

@app.route('/departments')
def departments_page():
    return render_template('departments.html')

@app.route('/departments/<int:dept_id>')
def department_detail_page(dept_id):
    try:
        dept = get_department_by_id(dept_id)
        return render_template('department_detail.html', department=dept)
    except ValueError:
        return render_template('404.html'), 404

@app.route('/alternatives')
def alternatives_page():
    return render_template('alternatives.html')

@app.route('/alternatives/<int:alt_id>/scores')
def alternative_scores_page(alt_id):
    try:
        alt = get_alternative_by_id(alt_id)
        return render_template('alternative_scores.html', alternative=alt)
    except ValueError:
        return render_template('404.html'), 404

@app.route('/import-export')
def import_export_page():
    return render_template('import_export.html')

# ============================================================
# API: Criteria
# ============================================================

@app.route('/api/criteria', methods=['GET'])
def api_get_criteria():
    try:
        criteria_list = get_all_criteria()
        return jsonify(criteria_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/criteria/<int:criteria_id>', methods=['GET'])
def api_get_criteria_by_id(criteria_id):
    try:
        crit = get_criteria_by_id(criteria_id)
        return jsonify(crit)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/criteria', methods=['POST'])
def api_create_criteria():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip() or None
        if not name:
            return jsonify({'error': 'Nama kriteria harus diisi'}), 400
        crit_id = create_criteria(name, description)
        return jsonify({'id': crit_id, 'message': 'Kriteria berhasil ditambahkan'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/criteria/<int:criteria_id>', methods=['PUT'])
def api_update_criteria(criteria_id):
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip() or None
        if not name:
            return jsonify({'error': 'Nama kriteria harus diisi'}), 400
        update_criteria(criteria_id, name, description)
        return jsonify({'message': 'Kriteria berhasil diupdate'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/criteria/<int:criteria_id>', methods=['DELETE'])
def api_delete_criteria(criteria_id):
    try:
        delete_criteria(criteria_id)
        return jsonify({'message': 'Kriteria berhasil dihapus'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# API: Departments
# ============================================================

@app.route('/api/departments', methods=['GET'])
def api_get_departments():
    try:
        departments = get_all_departments()
        result = []
        for dept in departments:
            profiles = get_department_profiles(dept['id'], active_only=False)
            dept['active_profiles'] = sum(1 for p in profiles if p['is_active'])
            result.append(dept)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/departments/<int:dept_id>', methods=['GET'])
def api_get_department(dept_id):
    try:
        dept = get_department_by_id(dept_id)
        return jsonify(dept)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/departments', methods=['POST'])
def api_create_department():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error': 'Nama departemen harus diisi'}), 400
        dept_id = create_department(name)
        return jsonify({'id': dept_id, 'message': 'Departemen berhasil ditambahkan'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/departments/<int:dept_id>', methods=['PUT'])
def api_update_department(dept_id):
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error': 'Nama departemen harus diisi'}), 400
        update_department(dept_id, name)
        return jsonify({'message': 'Departemen berhasil diupdate'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/departments/<int:dept_id>', methods=['DELETE'])
def api_delete_department(dept_id):
    try:
        delete_department(dept_id)
        return jsonify({'message': 'Departemen berhasil dihapus'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# API: Aspects
# ============================================================

@app.route('/api/aspects', methods=['GET'])
def api_get_aspects():
    try:
        aspects = get_all_aspects()
        return jsonify(aspects)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/aspects/<int:aspect_id>', methods=['GET'])
def api_get_aspect(aspect_id):
    try:
        asp = get_aspect_by_id(aspect_id)
        return jsonify(asp)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/aspects', methods=['POST'])
def api_create_aspect():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        weight = float(data.get('weight', 1.0))
        if not name:
            return jsonify({'error': 'Nama aspek harus diisi'}), 400
        asp_id = create_aspect(name, weight)
        return jsonify({'id': asp_id, 'message': 'Aspek berhasil ditambahkan'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/aspects/<int:aspect_id>', methods=['PUT'])
def api_update_aspect(aspect_id):
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        weight = float(data.get('weight', 1.0))
        if not name:
            return jsonify({'error': 'Nama aspek harus diisi'}), 400
        update_aspect(aspect_id, name, weight)
        return jsonify({'message': 'Aspek berhasil diupdate'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/aspects/<int:aspect_id>', methods=['DELETE'])
def api_delete_aspect(aspect_id):
    try:
        delete_aspect(aspect_id)
        return jsonify({'message': 'Aspek berhasil dihapus'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# API: Department Profiles
# ============================================================

@app.route('/api/departments/<int:dept_id>/profiles', methods=['GET'])
def api_get_profiles(dept_id):
    try:
        profiles = get_department_profiles(dept_id)
        return jsonify(profiles)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/departments/<int:dept_id>/profiles', methods=['POST'])
def api_add_profile(dept_id):
    try:
        data = request.get_json()
        criteria_id = data.get('criteria_id')
        target_value = data.get('target_value')
        weight = data.get('weight')
        type_ = data.get('type', 'secondary')
        aspect_id = data.get('aspect_id')

        if not all([criteria_id, target_value is not None, weight is not None]):
            return jsonify({'error': 'Semua field harus diisi'}), 400

        profile_id = add_department_profile(dept_id, int(criteria_id), float(target_value), float(weight), type_, aspect_id=aspect_id)
        clear_department_rankings(dept_id)
        return jsonify({'id': profile_id, 'message': 'Profil berhasil ditambahkan'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles/<int:profile_id>', methods=['PUT'])
def api_update_profile(profile_id):
    try:
        data = request.get_json()
        update_department_profile(
            profile_id,
            target_value=float(data['target_value']) if data.get('target_value') is not None else None,
            weight=float(data['weight']) if data.get('weight') is not None else None,
            type_=data.get('type'),
            is_active=data.get('is_active'),
            aspect_id=data.get('aspect_id')
        )
        return jsonify({'message': 'Profil berhasil diupdate'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles/<int:profile_id>', methods=['DELETE'])
def api_delete_profile(profile_id):
    try:
        delete_department_profile(profile_id)
        return jsonify({'message': 'Profil berhasil dihapus'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# API: Ranking
# ============================================================

@app.route('/api/departments/<int:dept_id>/ranking', methods=['GET'])
def api_get_ranking(dept_id):
    try:
        rankings = rank_alternatives(dept_id)
        return jsonify(rankings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# API: Alternatives
# ============================================================

@app.route('/api/alternatives', methods=['GET'])
def api_get_alternatives():
    try:
        alts = get_all_alternatives()
        return jsonify(alts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alternatives/<int:alt_id>', methods=['GET'])
def api_get_alternative(alt_id):
    try:
        alt = get_alternative_by_id(alt_id)
        return jsonify(alt)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alternatives', methods=['POST'])
def api_create_alternative():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        nim = data.get('nim', '').strip()
        prodi = data.get('prodi', '').strip()
        kelas = data.get('kelas', '').strip()
        additional_info = data.get('additional_info', '').strip() or None

        if not name:
            return jsonify({'error': 'Nama harus diisi'}), 400

        alt_id = create_alternative(name, nim, prodi, kelas, additional_info)
        clear_all_rankings()
        return jsonify({'id': alt_id, 'message': 'Alternatif berhasil ditambahkan'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alternatives/<int:alt_id>', methods=['PUT'])
def api_update_alternative(alt_id):
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        nim = data.get('nim', '').strip()
        prodi = data.get('prodi', '').strip()
        kelas = data.get('kelas', '').strip()
        additional_info = data.get('additional_info', '').strip() or None

        if not name:
            return jsonify({'error': 'Nama harus diisi'}), 400

        update_alternative(alt_id, name=name, nim=nim, prodi=prodi, kelas=kelas, additional_info=additional_info)
        clear_all_rankings()
        return jsonify({'message': 'Alternatif berhasil diupdate'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alternatives/<int:alt_id>', methods=['DELETE'])
def api_delete_alternative(alt_id):
    try:
        delete_alternative(alt_id)
        clear_all_rankings()
        return jsonify({'message': 'Alternatif berhasil dihapus'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# API: Alternative Scores
# ============================================================

@app.route('/api/alternatives/<int:alt_id>/scores', methods=['GET'])
def api_get_scores(alt_id):
    try:
        scores = get_alternative_scores(alt_id)
        return jsonify(scores)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alternatives/<int:alt_id>/scores', methods=['POST'])
def api_save_scores(alt_id):
    try:
        data = request.get_json()
        scores = data.get('scores', {})
        for criteria_id, value in scores.items():
            set_alternative_score(alt_id, int(criteria_id), float(value))
        clear_all_rankings()
        return jsonify({'message': 'Nilai berhasil disimpan'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# API: Export / Import Data
# ============================================================

def _collect_all_data():
    """Kumpulkan seluruh data dari Supabase untuk export."""
    criteria = get_all_criteria()
    departments = get_all_departments()
    department_profiles = []
    for d in departments:
        profiles = get_department_profiles(d["id"], active_only=False)
        department_profiles.extend(profiles)
    alternatives = get_all_alternatives()
    alternative_scores = []
    for a in alternatives:
        scores = get_alternative_scores(a["id"])
        for criteria_id, value in scores.items():
            alternative_scores.append({
                "alternative_id": a["id"],
                "criteria_id": criteria_id,
                "value": value
            })
    rankings = []
    for d in departments:
        try:
            dept_rankings = rank_alternatives(d["id"])
            rankings.append({
                "department_id": d["id"],
                "department_name": d["name"],
                "rankings": dept_rankings
            })
        except Exception:
            pass

    return {
        "criteria": criteria,
        "departments": departments,
        "department_profiles": department_profiles,
        "alternatives": alternatives,
        "alternative_scores": alternative_scores,
        "rankings": rankings
    }


def _get_rankings_per_department():
    """Ambil semua ranking per departemen untuk PDF laporan."""
    departments = get_all_departments()
    result = {}
    for d in departments:
        try:
            rankings = rank_alternatives(d["id"])
            result[d["name"]] = rankings
        except Exception:
            result[d["name"]] = []
    return result


@app.route('/api/export/json', methods=['GET'])
def api_export_json():
    """Export seluruh data ke format JSON."""
    try:
        data = _collect_all_data()
        json_str = export_to_json(
            criteria=data["criteria"],
            departments=data["departments"],
            department_profiles=data["department_profiles"],
            alternatives=data["alternatives"],
            alternative_scores=data["alternative_scores"],
            rankings=data["rankings"]
        )
        response = app.response_class(
            response=json_str,
            status=200,
            mimetype='application/json'
        )
        response.headers['Content-Disposition'] = 'attachment; filename=spk_export.json'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/pdf', methods=['GET'])
def api_export_pdf():
    """Export laporan lengkap ke PDF."""
    try:
        data = _collect_all_data()
        rankings_per_dept = _get_rankings_per_department()
        pdf_buf = export_all_data_to_pdf(
            criteria=data["criteria"],
            departments=data["departments"],
            alternatives=data["alternatives"],
            rankings_per_department=rankings_per_dept
        )
        response = app.response_class(
            response=pdf_buf.read(),
            status=200,
            mimetype='application/pdf'
        )
        response.headers['Content-Disposition'] = 'attachment; filename=spk_laporan.pdf'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/department/<int:dept_id>/pdf', methods=['GET'])
def api_export_department_pdf(dept_id):
    """Export ranking satu departemen ke PDF."""
    try:
        dept = get_department_by_id(dept_id)
        rankings = rank_alternatives(dept_id)
        criteria = get_all_criteria()
        pdf_buf = export_rankings_to_pdf(
            department_name=dept["name"],
            rankings=rankings,
            criteria_list=[c["name"] for c in criteria]
        )
        response = app.response_class(
            response=pdf_buf.read(),
            status=200,
            mimetype='application/pdf'
        )
        response.headers['Content-Disposition'] = f'attachment; filename=ranking_{dept["name"]}.pdf'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/pdf-report', methods=['GET'])
def api_export_pdf_report():
    """Export laporan lengkap TANPA perangkingan."""
    try:
        data = _collect_all_data()
        pdf_buf = export_report_without_rankings(
            criteria=data["criteria"],
            departments=data["departments"],
            alternatives=data["alternatives"],
            department_profiles=data["department_profiles"]
        )
        response = app.response_class(
            response=pdf_buf.read(),
            status=200,
            mimetype='application/pdf'
        )
        response.headers['Content-Disposition'] = 'attachment; filename=spk_laporan_data.pdf'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/rankings-all', methods=['GET'])
def api_export_rankings_all():
    """Export semua ranking per departemen ke ZIP berisi PDF masing-masing."""
    try:
        departments = get_all_departments()
        criteria = get_all_criteria()
        criteria_names = [c["name"] for c in criteria]

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for d in departments:
                try:
                    rankings = rank_alternatives(d["id"])
                    pdf_buf = export_rankings_to_pdf(
                        department_name=d["name"],
                        rankings=rankings,
                        criteria_list=criteria_names
                    )
                    safe_name = d["name"].replace(" ", "_").replace("/", "_")
                    zf.writestr(f"ranking_{safe_name}.pdf", pdf_buf.read())
                except Exception:
                    continue

        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='semua_ranking.zip'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/import/json', methods=['POST'])
def api_import_json():
    """Import data dari file JSON."""
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({'error': 'Data JSON tidak valid'}), 400

        # Validasi data
        errors = validate_import_data(data)
        if errors:
            return jsonify({'error': 'Validasi gagal', 'details': errors}), 400

        # 1. Import criteria
        criteria_map = {}
        for c in data.get("criteria", []):
            try:
                new_id = create_criteria(c["name"], c.get("description"))
                criteria_map[c.get("id")] = new_id
            except Exception:
                pass

        # 2. Import departments
        dept_map = {}
        for d in data.get("departments", []):
            try:
                new_id = create_department(d["name"])
                dept_map[d.get("id")] = new_id
            except Exception:
                pass

        # 3. Import department_profiles
        for p in data.get("department_profiles", []):
            try:
                dept_id = dept_map.get(p["department_id"])
                crit_id = criteria_map.get(p["criteria_id"])
                if dept_id and crit_id:
                    add_department_profile(
                        dept_id, crit_id,
                        p["target_value"], p["weight"], p["type"]
                    )
            except Exception:
                pass

        # 4. Import alternatives
        alt_map = {}
        for a in data.get("alternatives", []):
            try:
                new_id = create_alternative(
                    a["name"], a.get("nim", ""),
                    a.get("prodi", ""), a.get("kelas", ""),
                    a.get("additional_info")
                )
                alt_map[a.get("id")] = new_id
            except Exception:
                pass

        # 5. Import alternative_scores
        for s in data.get("alternative_scores", []):
            try:
                alt_id = alt_map.get(s["alternative_id"])
                crit_id = criteria_map.get(s["criteria_id"])
                if alt_id and crit_id:
                    set_alternative_score(alt_id, crit_id, s["value"])
            except Exception:
                pass

        clear_all_rankings()
        return jsonify({'message': 'Import berhasil', 'detail': {
            'criteria': len(criteria_map),
            'departments': len(dept_map),
            'alternatives': len(alt_map)
        }}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, port=5000)