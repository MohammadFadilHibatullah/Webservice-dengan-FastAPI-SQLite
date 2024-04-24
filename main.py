# conda activate webservicep2plending webservicep2plending
# uvicorn main:app --reload


# Import modul yang diperlukan
from typing import Union  # Mengimpor Union untuk mendefinisikan tipe data gabungan
from fastapi import FastAPI, Response, Request, HTTPException  # Mengimpor kelas-kelas yang diperlukan dari FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Mengimpor middleware CORS dari FastAPI
import sqlite3  # Mengimpor modul sqlite3 untuk interaksi dengan database SQLite

# Inisialisasi aplikasi FastAPI
app = FastAPI()

# Menambahkan middleware CORS untuk menangani permintaan lintas domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mengizinkan akses dari semua domain
    allow_credentials=True,  # Mengizinkan kredensial
    allow_methods=["*"],  # Mengizinkan semua metode HTTP
    allow_headers=["*"],  # Mengizinkan semua header HTTP
)

# Definisi endpoint untuk route "/" dengan method GET
@app.get("/")
def read_root():
    return {"Hello": "World"}  # Mengembalikan objek JSON dengan pesan "Hello World"

# Definisi endpoint untuk route "/mahasiswa/{nim}" dengan method GET
@app.get("/mahasiswa/{nim}")
def ambil_mhs(nim: str):
    return {"nama": "Budi Martami"}  # Mengembalikan objek JSON dengan nama mahasiswa "Budi Martami"

# Definisi endpoint untuk route "/mahasiswa2/" dengan method GET
@app.get("/mahasiswa2/")
def ambil_mhs2(nim: str):
    return {"nama": "Budi Martami 2"}  # Mengembalikan objek JSON dengan nama mahasiswa "Budi Martami 2"

# Definisi endpoint untuk route "/daftar_mhs/" dengan method GET
@app.get("/daftar_mhs/")
def daftar_mhs(id_prov: str, angkatan: str):
    # Mengembalikan objek JSON yang berisi query parameter dan data mahasiswa
    return {
        "query": f"idprov: {id_prov}; angkatan: {angkatan}",  # Mengembalikan string yang berisi query parameter
        "data": [{"nim": "1234"}, {"nim": "1235"}]  # Mengembalikan data dalam bentuk list mahasiswa
    }

# Definisi endpoint untuk route "/init/" dengan method GET
@app.get("/init/")
def init_db():
    try:
        # Membuat koneksi ke database SQLite
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        # Membuat tabel 'mahasiswa' jika belum ada
        create_table = """ CREATE TABLE mahasiswa(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            nim TEXT NOT NULL,
            nama TEXT NOT NULL,
            id_prov TEXT NOT NULL,
            angkatan TEXT NOT NULL,
            tinggi_badan INTEGER
        )"""
        cur.execute(create_table)
        con.commit()
    except:
        return {"status": "terjadi error"}  # Mengembalikan pesan error jika terjadi kesalahan
    finally:
        con.close()  # Menutup koneksi database
    return {"status": "ok, db dan tabel berhasil dicreate"}  # Mengembalikan pesan berhasil jika tidak ada kesalahan

# Import modul BaseModel dari Pydantic untuk mendefinisikan model data
from pydantic import BaseModel

# Import modul Optional dari typing untuk mendefinisikan parameter opsional
from typing import Optional

# Definisikan model data Mahasiswa
class Mhs(BaseModel):
    nim: str
    nama: str
    id_prov: str
    angkatan: str
    tinggi_badan: Optional[int] | None = None  # yang boleh null hanya tinggi_badan

# Definisi endpoint untuk route "/tambah_mhs/" dengan method POST
@app.post("/tambah_mhs/", response_model=Mhs, status_code=201)  
def tambah_mhs(m: Mhs, response: Response, request: Request):
    try:
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        # Menambahkan data mahasiswa ke dalam tabel 'mahasiswa'
        cur.execute("""insert into mahasiswa (nim, nama, id_prov, angkatan, tinggi_badan) values ("{}", "{}", "{}", "{}", {})""".format(m.nim, m.nama, m.id_prov, m.angkatan, m.tinggi_badan))
        con.commit()  # Melakukan commit untuk menyimpan perubahan
    except:
        print("oioi error")
        return {"status": "terjadi error"}  # Mengembalikan pesan error jika terjadi kesalahan
    finally:
        con.close()  # Menutup koneksi database
    response.headers["Location"] = "/mahasiswa/{}".format(m.nim)  # Menetapkan header Location pada respons
    print(m.nim)
    print(m.nama)
    print(m.angkatan)
    return m  # Mengembalikan data mahasiswa yang ditambahkan

# Definisi endpoint untuk route "/tampilkan_semua_mhs/" dengan method GET
@app.get("/tampilkan_semua_mhs/")
def tampil_semua_mhs():
    try:
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        recs = []
        # Mengambil semua data mahasiswa dari tabel 'mahasiswa'
        for row in cur.execute("select * from mahasiswa"):
            recs.append(row)
    except:
        return {"status": "terjadi error"}  # Mengembalikan pesan error jika terjadi kesalahan
    finally:
        con.close()  # Menutup koneksi database
    return {"data": recs}  # Mengembalikan data mahasiswa

# Import modul jsonable_encoder dari fastapi.encoders
from fastapi.encoders import jsonable_encoder

# Definisi endpoint untuk route "/update_mhs_put/{nim}" dengan method PUT
@app.put("/update_mhs_put/{nim}", response_model=Mhs)
def update_mhs_put(response: Response, nim: str, m: Mhs):
    try:
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        # Memeriksa apakah data mahasiswa dengan nim tertentu ada dalam tabel 'mahasiswa'
        cur.execute("select * from mahasiswa where nim = ?", (nim,))
        existing_item = cur.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))  # Mengembalikan pesan error jika terjadi kesalahan
    if existing_item:  # Jika data ada, lakukan update
        print(m.tinggi_badan)
        cur.execute("update mahasiswa set nama = ?, id_prov = ?, angkatan=?, tinggi_badan=? where nim=?", (m.nama, m.id_prov, m.angkatan, m.tinggi_badan, nim))
        con.commit()  # Melakukan commit untuk menyimpan perubahan
        response.headers["location"] = "/mahasiswa/{}".format(m.nim)  # Menetapkan header Location pada respons
    else:  # Jika data tidak ada, kirimkan respons dengan status code 404
        print("item not found")
        raise HTTPException(status_code=404, detail="Item Not Found")
    con.close()  # Menutup koneksi database
    return m  # Mengembalikan data mahasiswa yang telah diupdate

# Definisi model data MhsPatch untuk method PATCH
class MhsPatch(BaseModel):
    nama: str | None = "kosong"
    id_prov: str | None = "kosong"
    angkatan: str | None = "kosong"
    tinggi_badan: Optional[int] | None = -9999  # yang boleh null hanya tinggi_badan

# Definisi endpoint untuk route "/update_mhs_patch/{nim}" dengan method PATCH
@app.patch("/update_mhs_patch/{nim}", response_model=MhsPatch)
def update_mhs_patch(response: Response, nim: str, m: MhsPatch):
    try:
        print(str(m))
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("select * from mahasiswa where nim = ?", (nim,))
        existing_item = cur.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))  # Mengembalikan pesan error jika terjadi kesalahan
    if existing_item:  # Jika data ada, lakukan update
        sqlstr = "update mahasiswa set "
        if m.nama != "kosong":
            if m.nama != None:
                sqlstr = sqlstr + " nama = '{}' ,".format(m.nama)
            else:
                sqlstr = sqlstr + " nama = null ,"
        if m.angkatan != "kosong":
            if m.angkatan != None:
                sqlstr = sqlstr + " angkatan = '{}' ,".format(m.angkatan)
            else:
                sqlstr = sqlstr + " angkatan = null ,"
        if m.id_prov != "kosong":
            if m.id_prov != None:
                sqlstr = sqlstr + " id_prov = '{}' ,".format(m.id_prov)
            else:
                sqlstr = sqlstr + " id_prov = null, "
        if m.tinggi_badan != -9999:
            if m.tinggi_badan != None:
                sqlstr = sqlstr + " tinggi_badan = {} ,".format(m.tinggi_badan)
            else:
                sqlstr = sqlstr + " tinggi_badan = null ,"
        sqlstr = sqlstr[:-1] + " where nim='{}' ".format(nim)
        print(sqlstr)
        try:
            cur.execute(sqlstr)
            con.commit()
            response.headers["location"] = "/mahasixswa/{}".format(nim)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))
    else:  # Jika data tidak ada, kirimkan respons dengan status code 404
        raise HTTPException(status_code=404, detail="Item Not Found")
    con.close()  # Menutup koneksi database
    return m  # Mengembalikan data mahasiswa yang telah diupdate

# Definisi endpoint untuk route "/delete_mhs/{nim}" dengan method DELETE
@app.delete("/delete_mhs/{nim}")
def delete_mhs(nim: str):
    try:
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        # Menghapus data mahasiswa dengan nim tertentu dari tabel 'mahasiswa'
        sqlstr = "delete from mahasiswa  where nim='{}'".format(nim)
        print(sqlstr)  # Debugging
        cur.execute(sqlstr)
        con.commit()  # Melakukan commit untuk menyimpan perubahan
    except:
        return {"status": "terjadi error"}  # Mengembalikan pesan error jika terjadi kesalahan
    finally:
        con.close()  # Menutup koneksi database
    return {"status": "ok"}  # Mengembalikan pesan berhasil jika tidak ada kesalahan
