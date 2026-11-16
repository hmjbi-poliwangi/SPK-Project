"""
Helper autentikasi untuk Flask session-based auth.
"""

from functools import wraps
from flask import session, redirect, url_for, request, jsonify


VALID_ROLES = ('developer', 'kahim', 'co', 'anggota')


def login_required(f):
    """Decorator: wajib login untuk mengakses halaman."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized'}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(allowed_roles):
    """Decorator factory: wajib role tertentu untuk mengakses halaman."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'error': 'Unauthorized'}), 401
                return redirect(url_for('login_page'))
            if session.get('role') not in allowed_roles:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'error': 'Forbidden'}), 403
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def developer_required(f):
    """Decorator: wajib role developer."""
    return role_required(('developer',))(f)


def kahim_required(f):
    """Decorator: wajib role kahim."""
    return role_required(('kahim',))(f)


def co_required(f):
    """Decorator: wajib role co."""
    return role_required(('co',))(f)


def anggota_required(f):
    """Decorator: wajib role anggota."""
    return role_required(('anggota',))(f)


def get_current_user() -> dict | None:
    """Return data user dari session, atau None jika belum login."""
    if 'user_id' not in session:
        return None
    return {
        'id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role'),
        'department_id': session.get('department_id'),
    }


def is_logged_in() -> bool:
    """Cek apakah user sudah login."""
    return 'user_id' in session


def is_developer() -> bool:
    """Cek apakah user yang login adalah developer."""
    return session.get('role') == 'developer'


def is_kahim() -> bool:
    """Cek apakah user yang login adalah kahim."""
    return session.get('role') == 'kahim'


def is_co() -> bool:
    """Cek apakah user yang login adalah co."""
    return session.get('role') == 'co'


def is_anggota() -> bool:
    """Cek apakah user yang login adalah anggota."""
    return session.get('role') == 'anggota'


def can_access_department(department_id: int) -> bool:
    """Cek apakah user yang login dapat mengakses departemen tertentu."""
    role = session.get('role')
    if role in ('developer', 'kahim'):
        return True
    return session.get('department_id') == department_id


def can_modify_department(department_id: int) -> bool:
    """Cek apakah user yang login dapat mengubah data departemen tertentu."""
    role = session.get('role')
    if role == 'developer':
        return True
    if role == 'co':
        return session.get('department_id') == department_id
    return False
