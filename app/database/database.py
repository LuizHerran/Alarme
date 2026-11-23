import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "alarme.db"


def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection

def initialize_database():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            arquivo TEXT NOT NULL,
            inicio REAL NOT NULL DEFAULT 0,
            duracao REAL NOT NULL DEFAULT 15,
            fade_in REAL NOT NULL DEFAULT 1,
            fade_out REAL NOT NULL DEFAULT 1,
            criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alarmes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            horario TEXT NOT NULL,
            audio_id INTEGER NOT NULL,
            ativo INTEGER NOT NULL DEFAULT 1,

            FOREIGN KEY (audio_id)
                REFERENCES audios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alarme_dias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alarme_id INTEGER NOT NULL,
            dia_semana INTEGER NOT NULL,

            FOREIGN KEY (alarme_id)
                REFERENCES alarmes(id)
                ON DELETE CASCADE
        )
    """)

    connection.commit()
    connection.close()

def insert_audio(
    nome: str,
    arquivo: str,
    inicio: float,
    duracao: float,
    fade_in: float,
    fade_out: float
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO audios (
            nome,
            arquivo,
            inicio,
            duracao,
            fade_in,
            fade_out
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            nome,
            arquivo,
            inicio,
            duracao,
            fade_in,
            fade_out
        )
    )

    audio_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return audio_id

def get_all_audios():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM audios
        ORDER BY nome COLLATE NOCASE
    """)

    audios = cursor.fetchall()

    connection.close()

    return audios

def get_audio(audio_id: int):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM audios
        WHERE id = ?
        """,
        (audio_id,)
    )

    audio = cursor.fetchone()

    connection.close()

    return audio

def update_audio(
    audio_id: int,
    nome: str,
    arquivo: str,
    inicio: float,
    duracao: float,
    fade_in: float,
    fade_out: float
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE audios
        SET
            nome = ?,
            arquivo = ?,
            inicio = ?,
            duracao = ?,
            fade_in = ?,
            fade_out = ?
        WHERE id = ?
        """,
        (
            nome,
            arquivo,
            inicio,
            duracao,
            fade_in,
            fade_out,
            audio_id
        )
    )

    connection.commit()
    connection.close()

def delete_audio(audio_id: int):
    connection = get_connection()

    cursor = connection.cursor()

    # Verifica se o áudio está sendo usado por algum alarme
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM alarmes
        WHERE audio_id = ?
        """,
        (audio_id,)
    )

    result = cursor.fetchone()

    if result[0] > 0:
        connection.close()

        raise ValueError(
            "Este áudio está sendo usado por um alarme "
            "e não pode ser excluído."
        )

    cursor.execute(
        """
        DELETE FROM audios
        WHERE id = ?
        """,
        (audio_id,)
    )

    connection.commit()
    connection.close()

def insert_alarm(
    nome: str,
    horario: str,
    audio_id: int,
    dias: list[int]
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO alarmes (
            nome,
            horario,
            audio_id,
            ativo
        )
        VALUES (?, ?, ?, 1)
        """,
        (
            nome,
            horario,
            audio_id
        )
    )

    alarm_id = cursor.lastrowid

    for dia in dias:
        cursor.execute(
            """
            INSERT INTO alarme_dias (
                alarme_id,
                dia_semana
            )
            VALUES (?, ?)
            """,
            (
                alarm_id,
                dia
            )
        )

    connection.commit()
    connection.close()

    return alarm_id


def get_all_alarms():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            alarmes.*,
            audios.nome AS audio_nome
        FROM alarmes
        INNER JOIN audios
            ON audios.id = alarmes.audio_id
        ORDER BY alarmes.horario
        """
    )

    alarms = cursor.fetchall()

    connection.close()

    return alarms


def get_alarm_days(alarm_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT dia_semana
        FROM alarme_dias
        WHERE alarme_id = ?
        ORDER BY dia_semana
        """,
        (alarm_id,)
    )

    days = [
        row["dia_semana"]
        for row in cursor.fetchall()
    ]

    connection.close()

    return days


def get_alarm(alarm_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM alarmes
        WHERE id = ?
        """,
        (alarm_id,)
    )

    alarm = cursor.fetchone()

    connection.close()

    return alarm

def update_alarm(
    alarm_id: int,
    nome: str,
    horario: str,
    audio_id: int,
    dias: list[int]
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE alarmes
        SET nome = ?,
            horario = ?,
            audio_id = ?
        WHERE id = ?
        """,
        (
            nome,
            horario,
            audio_id,
            alarm_id
        )
    )

    cursor.execute(
        """
        DELETE FROM alarme_dias
        WHERE alarme_id = ?
        """,
        (alarm_id,)
    )

    for dia in dias:
        cursor.execute(
            """
            INSERT INTO alarme_dias (
                alarme_id,
                dia_semana
            )
            VALUES (?, ?)
            """,
            (
                alarm_id,
                dia
            )
        )

    connection.commit()
    connection.close()

def set_alarm_active(alarm_id: int, ativo: bool):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE alarmes
        SET ativo = ?
        WHERE id = ?
        """,
        (
            1 if ativo else 0,
            alarm_id
        )
    )

    connection.commit()
    connection.close()

def delete_alarm(alarm_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM alarme_dias
        WHERE alarme_id = ?
        """,
        (alarm_id,)
    )

    cursor.execute(
        """
        DELETE FROM alarmes
        WHERE id = ?
        """,
        (alarm_id,)
    )

    connection.commit()
    connection.close()

if __name__ == "__main__":
    initialize_database()
    print(f"Banco criado em: {DB_PATH}")
    
