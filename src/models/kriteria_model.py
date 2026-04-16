class Kriteria :
  def __init__(self, kode, nama, bobot, jenis):
    self.kode = kode
    self.nama = nama
    self.bobot = bobot
    self.jenis = jenis
  
  def obj_to_dict(self):
    return {
      "kode" : self.kode,
      "nama" : self.nama,
      "bobot" : self.bobot,
      "jenis" : self.jenis
    }

class CriteriaManager:
  def __init__(self):
    self.daftar_kriteria = []

  def add_criteria(self, kriteria_obj):
    self.daftar_kriteria.append(kriteria_obj)

  def get_all_criteria(self):
    return self.daftar_kriteria
  
  def weight_total(self):
    return sum(k.bobot for k in self.daftar_kriteria)