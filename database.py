import sqlite3
import sys


class DataBase:

    def __init__(self):
        self._conn = None

    def conectar(self):
        '''
            realiza la conexion a la base de datos
            retorna True si la conexion fue exitosa
        '''
        try:
            self._conn = sqlite3.connect('test.db')
            return True
        except:
            print sys.exc_info()[1]
            return False

    def _verifica_conexion(self):
        '''
            verifica que se haya realizado una conexion a la base de datos
            retorna True si ya se realizo la conexion
        '''
        if not self._conn:
            print "Error. Todavia no se ha conectado a la base de datos"
            return False
        return True

    def init(self):
        if not self._verifica_conexion():
            return False
        cur = self._conn.cursor()
        print("Base de datos abierta")
        cur.execute("PRAGMA table_info(stub)")
        data = cur.fetchall()
        print(data)
        if len(data) == 0:
            print("Tabla vacia")
            cur.execute("""
            CREATE TABLE stub(
            stub_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre          TEXT    NOT NULL,
            cal_rapid_id    INT
            )""")
            cur.execute("""
            CREATE TABLE cal_rapid(
            cal_rapid_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            cal_1           REAL,
            cal_2           REAL,
            cal_3           REAL,
            cal_4           REAL,
            cal_5           REAL,
            cal_6           REAL,
            cal_7           REAL,
            cal_8           REAL
            )""")
            cur.execute("""
            CREATE TABLE cal_precision(
            cal_precision_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            stub_id             INT,
            frecuencia          REAL
            )""")
            cur.execute("""
            CREATE TABLE medicion_precision(
            cal_precision_id    INT,
            valor               REAL,
            valor_id            INT
            )""")
            self._conn.commit()
        cur.execute("PRAGMA table_info(stub)")
        data = cur.fetchall()
        print(data)
        cur.close()

    def listar(self, args1, args2):
        '''
            lista la tabla Artist
            retorna True si pudo realizar la operacion exitosamente
        '''
        if not self._verifica_conexion():
            return False
        error = False
        try:
            cur = self._conn.cursor()
#            print("SELECT * FROM %s" % tabla)
            cur.execute("SELECT %s FROM %s" % (args2,args1))
#            print(cur.fetchall())
            return cur.fetchall()
            #for id, name in cur.fetchall():
            #    print "%d\t%s" % (id, name)
        except:
            print sys.exc_info()[1]
            error = True
        finally:
            cur.close()
        return error

    def agregar_stub(self,args):
        cur = self._conn.cursor()
        cur.execute("INSERT INTO stub(nombre) VALUES (?)", (args,))
        self._conn.commit()
        cur.close()

    def agregar_calibracion_rapida(self,calibracion,stub):
        cur = self._conn.cursor()
        cur.execute("INSERT INTO cal_rapid(cal_1,cal_2,cal_3,cal_4,cal_5,cal_6,cal_7,cal_8) VALUES (?,?,?,?,?,?,?,?)", (calibracion))
        self._conn.commit()
        cur.execute("SELECT MAX(cal_rapid_id) FROM cal_rapid")
        data = cur.fetchone()
        print(data)
        cur.execute("UPDATE stub SET cal_rapid_id=? WHERE nombre = '%s'"%stub, (data))
        self._conn.commit()
        cur.close()

    def lectura_calibracion_rapida(self,stub):
        cur = self._conn.cursor()
        cur.execute("SELECT cal_rapid_id FROM stub WHERE nombre = '%s'"%stub)
        data = cur.fetchone()
        print(data)
        cur.execute("SELECT * FROM cal_rapid WHERE cal_rapid_id=?", (data))
        mediciones = cur.fetchall()
        cur.close()
        return mediciones

    def borrar_stub(self,stub):
        cur = self._conn.cursor()
        cur.execute("SELECT stub_id FROM stub WHERE nombre = '%s'" % stub)
        sutbid=cur.fetchone()
        cur.execute("SELECT cal_rapid_id FROM stub WHERE nombre = '%s'" % stub)
        rapidid=cur.fetchone()
        cur.execute("SELECT cal_precision_id FROM cal_precision WHERE stub_id = ?",  sutbid)
        medid=cur.fetchone()
        cur.execute("DELETE FROM stub WHERE nombre = '%s'" % stub)
        cur.execute("DELETE FROM cal_rapid WHERE cal_rapid_id = '%s'" % rapidid)
        cur.execute("DELETE FROM cal_precision WHERE stub_id = '%s'" % sutbid)
        cur.execute("DELETE FROM medicion_precision WHERE cal_precision_id = '%s'" % medid)
        self._conn.commit()
        cur.close()


if __name__ == '__main__':

    clase_sqlite = DataBase()

    clase_sqlite.conectar()
    #clase_sqlite.init()
    #clase_sqlite.agregar_stub("MONGO")
    clase_sqlite.listar("stub","nombre")
    clase_sqlite.agregar_stub("Tongo")
    clase_sqlite.listar("stub","nombre")
    #clase_sqlite.listar("cal_rapid")
    #mediciones = (1,2,3,5,8,13,21,34)
    #clase_sqlite.agregar_calibracion_rapida(mediciones, str("CHONGO"))
    #clase_sqlite.listar("stub")
    _cal_5ghz = clase_sqlite.lectura_calibracion_rapida(str("CHONGO"))
    print(_cal_5ghz[0][5])
