
import pyodbc
from datetime import datetime
# ===========================================================
#   BLOC DATABASE SQL SERVER INTEGRE 
# ===========================================================


class Database:
    _config = None

    @classmethod
    def init_from_config(cls, config):
        cls._config = config
    """
    Gestionnaire centralisé pour toutes les opérations SQL Server
    via DSN 'EXTENSIONS_WINPASS_RW_64' en authentification Windows.
    """

    @classmethod
    def get_connection(cls):
        if cls._config is None:
            raise RuntimeError("Database non initialisée avec la config")
        
        dsn = cls._config["dsn"]

        conn_str = (
            f"DSN={dsn};"
            f"Trusted_Connection=yes;"
        )

        return pyodbc.connect(conn_str)


    # -----------------------------------------
    #  SERVICE : [WINPASS01\INSTANCEWP012K8].[EXTENSIONS_WINPASS].dbo.[DW2VE_Structure]
    # -----------------------------------------
    def get_service(cls): # type: ignore
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT distinct SUBSTRING([Niveau1], 10, len([Niveau1])) as service  FROM DW2VE_Structure where Niveau1 is not null order by 1")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows


    # -----------------------------------------
    #  LOTS : CRUD
    # -----------------------------------------

    @staticmethod
    def lot_exists(id_lot):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_lot FROM LOTS WHERE id_lot = ?", id_lot)
        exists = cur.fetchone() is not None
        cur.close()
        conn.close()
        return exists

    @staticmethod
    def create_or_update_lot(id_lot, numero_boite, date_creation, created_by,
                             ouvert_par=None, ouvert_le=None,
                             verrouille=0, date_livraison=None):

        conn = Database.get_connection()
        cur = conn.cursor()

        if Database.lot_exists(id_lot):
            cur.execute("""
                UPDATE LOTS 
                SET numero_boite=?, date_creation=?, created_by=?, 
                    ouvert_par=?, ouvert_le=?, verrouille=?, date_livraison=?
                WHERE id_lot=?
            """, (numero_boite, date_creation, created_by,
                  ouvert_par, ouvert_le, verrouille, date_livraison,
                  id_lot))

        else:
            cur.execute("""
                INSERT INTO LOTS (id_lot, numero_boite, date_creation, created_by,
                                  ouvert_par, ouvert_le, verrouille, date_livraison)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (id_lot, numero_boite, date_creation, created_by,
                  ouvert_par, ouvert_le, verrouille, date_livraison))

        cur.close()
        conn.close()

    @staticmethod
    def set_lot_locked(id_lot, locked=True):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE LOTS SET verrouille=? WHERE id_lot=?",
                    (1 if locked else 0, id_lot))
        cur.close()
        conn.close()

    @staticmethod
    def set_lot_livraison(id_lot, date_heure):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE LOTS SET date_livraison=? WHERE id_lot=?",
                    (date_heure, id_lot))
        cur.close()
        conn.close()

    # -----------------------------------------
    #  PLIS : CRUD
    # -----------------------------------------

    @staticmethod
    def insert_pli(id_lot, numero_pli, est_lu, numero_boite, pole, complexe, gestionnaire):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO PLIS (id_lot, numero_pli, est_lu, numero_boite, pole, complexe, gestionnaire)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_lot, numero_pli, est_lu, numero_boite, pole, complexe, gestionnaire))
        cur.close()
        conn.close()

    @staticmethod
    def set_pli_lu(id_lot, numero_pli, est_lu=True):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE PLIS SET est_lu=?
            WHERE id_lot=? AND numero_pli=?
        """, (1 if est_lu else 0, id_lot, numero_pli))
        cur.close()
        conn.close()

    @staticmethod
    def get_plis(id_lot):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id_pli, id_lot, numero_pli, est_lu, numero_boite,
                   pole, complexe, gestionnaire
            FROM PLIS
            WHERE id_lot=?
            ORDER BY numero_pli
        """, (id_lot,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    # -----------------------------------------
    #  HISTORIQUE
    # -----------------------------------------

    @staticmethod
    def add_histo(id_lot, action, utilisateur, numero_pli=None, numero_boite=None):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO HISTORIQUE 
                (id_lot, numero_pli, numero_boite, action, utilisateur, date_action)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_lot, numero_pli, numero_boite, action, utilisateur, datetime.now()))
        cur.close()
        conn.close()