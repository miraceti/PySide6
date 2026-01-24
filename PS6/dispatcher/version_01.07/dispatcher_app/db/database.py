import pyodbc
import re
from datetime import datetime
from PySide6.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery


class Database:
    _config = None

    # ===========================================================
    #  INITIALISATION
    # ===========================================================

    @classmethod
    def init_from_config(cls, config):
        cls._config = config

    # ===========================================================
    #  CONNEXION PYODBC (METIER / CRUD)
    # ===========================================================

    @classmethod
    def get_connection(cls):
        if cls._config is None:
            raise RuntimeError("Database non initialisée avec la config")

        dsn = cls._config["dsn"]
        conn_str = f"DSN={dsn};Trusted_Connection=yes;"
        return pyodbc.connect(conn_str)

    # ===========================================================
    #  CONNEXION QT SQL (UI / MODELES)
    # ===========================================================

    @classmethod
    def get_qt_connection_1(cls, connection_name="qt_main"):
        if cls._config is None:
            raise RuntimeError("Database non initialisée avec la config")

        dsn = cls._config["dsn"]

        if QSqlDatabase.contains(connection_name):
            db = QSqlDatabase.database(connection_name)
        else:
            db = QSqlDatabase.addDatabase("QODBC", connection_name)
            db.setDatabaseName(f"DSN={dsn};Trusted_Connection=yes;")

        if not db.open():
            raise RuntimeError(db.lastError().text())

        return db
    

    @classmethod
    def get_qt_connection(cls, connection_name="qt_main"):
        """
        Connexion Qt QODBC DSN-less pour MSSQL.
        Lit le serveur et la base depuis la config.ini.
        """
        if cls._config is None:
            raise RuntimeError("Database non initialisée avec la config")

        # lecture des paramètres dans la section PARAMS
        server = cls._config["server"]
        database = cls._config["database"]

        if not server or not database:
            raise RuntimeError(
                "La config doit contenir server et database pour la connexion DSN-less"
            )

        # réutilisation si la connexion existe déjà
        if QSqlDatabase.contains(connection_name):
            db = QSqlDatabase.database(connection_name)
        else:
            db = QSqlDatabase.addDatabase("QODBC", connection_name)
            db.setDatabaseName(
                f"Driver={{ODBC Driver 17 for SQL Server}};"
                f"Server={server};"
                f"Database={database};"
                f"Trusted_Connection=yes;"
            )

        if not db.open():
            raise RuntimeError(f"Impossible de se connecter : {db.lastError().text()}")

        return db


    # ===========================================================
    #  FULL-TEXT SEARCH (REUTILISABLE PARTOUT)
    # ===========================================================
    @classmethod
    def fulltext_search_complexe(
        cls,
        text: str,
        limit: int = 50
    ) -> QSqlQueryModel:
        
        if cls._config is None:
            raise RuntimeError("Database non initialisée")

        # params = cls._config["PARAMS"]

        # table = params["fulltext_table_p"]
        # column = params["fulltext_column_p1"]

        table = cls._config["fulltext_table_p"]
        column = cls._config["fulltext_column_p1"]

        # db = cls.get_qt_connection()
        db = Database.get_qt_connection()

        model = QSqlQueryModel()

        text = re.sub(r"[^\w\s]", " ", text).strip()

        # Cas texte trop court → modèle vide
        if len(text) < 2:
            model.setQuery(
                f"SELECT TOP 0 id, {column} FROM {table}",
                db
            )
            return model

        terms = text.split()
        fts = " AND ".join(f'"{t}*"' for t in terms)

        sql = f"""
            SELECT TOP {limit}
                id,
                {column}
            FROM {table}
            WHERE CONTAINS({column}, ?)
        """

        query = QSqlQuery(db)
        query.prepare(sql)
        query.addBindValue(fts)

        if not query.exec():
            raise RuntimeError(query.lastError().text())

        model.setQuery(query)
        return model

    # ===========================================================
    #  FONCTION QUI RENVOI UNE LISTE
    # ===========================================================
    @classmethod
    def fulltext_search_complexe_list(cls, text: str, limit: int = 50) -> list[str]:
        """
        Recherche full-text sur DW2VE_production.Complexe
        Retourne une liste de chaînes pour QListWidget
        """
        
        table = cls._config["fulltext_table_p"] # type: ignore
        column = cls._config["fulltext_column_p1"] # type: ignore

        db = cls.get_qt_connection()

        text = re.sub(r"[^\w\s]", " ", text).strip()
        if len(text) < 2:
            return []

        terms = text.split()
        fts = " AND ".join(f'"{t}*"' for t in terms)

        sql = f"""
            SELECT TOP {limit} {column}
            FROM {table}
            WHERE CONTAINS({column}, ?)
            ORDER BY {column}
        """

        query = QSqlQuery(db)
        query.prepare(sql)
        query.addBindValue(fts)
        query.exec()

        results = []
        while query.next():
            results.append(query.value(0))  # la colonne Complexe
        return results



    # ===========================================================
    #  SERVICES EXISTANTS (PYODBC)
    # ===========================================================

    @classmethod
    def get_service(cls):
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT SUBSTRING([Niveau1], 10, LEN([Niveau1])) AS service
            FROM DW2VE_Structure
            WHERE Niveau1 IS NOT NULL
            ORDER BY 1
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    # ===========================================================
    #  LOTS
    # ===========================================================

    @staticmethod
    def lot_exists(id_lot):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM LOTS WHERE id_lot = ?", id_lot)
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
                INSERT INTO LOTS (
                    id_lot, numero_boite, date_creation, created_by,
                    ouvert_par, ouvert_le, verrouille, date_livraison
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (id_lot, numero_boite, date_creation, created_by,
                  ouvert_par, ouvert_le, verrouille, date_livraison))

        conn.commit()
        cur.close()
        conn.close()

    # ===========================================================
    #  PLIS
    # ===========================================================

    @staticmethod
    def insert_pli(id_lot, numero_pli, est_lu, numero_boite, pole, complexe, gestionnaire):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO PLIS (
                id_lot, numero_pli, est_lu,
                numero_boite, pole, complexe, gestionnaire
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_lot, numero_pli, est_lu, numero_boite, pole, complexe, gestionnaire))
        conn.commit()
        cur.close()
        conn.close()

    # ===========================================================
    #  HISTORIQUE
    # ===========================================================

    @staticmethod
    def add_histo(id_lot, action, utilisateur, numero_pli=None, numero_boite=None):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO HISTORIQUE (
                id_lot, numero_pli, numero_boite,
                action, utilisateur, date_action
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_lot, numero_pli, numero_boite,
              action, utilisateur, datetime.now()))
        conn.commit()
        cur.close()
        conn.close()
