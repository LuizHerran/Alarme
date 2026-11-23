from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from pathlib import Path
from app.audio.processor import AudioProcessor
from app.database.database import get_all_alarms, get_audio, get_alarm_days


class AlarmScheduler:

    def __init__(self):

        self.scheduler = BackgroundScheduler()

        # Guarda os alarmes que já foram executados
        # no minuto atual.
        self.executed_alarms = set()

    def start(self):

        if self.scheduler.running:
            return

        self.scheduler.add_job(
            self.check_alarms,
            "interval",
            seconds=1,
            id="alarm_checker",
            replace_existing=True
        )

        self.scheduler.start()

        print("Scheduler iniciado.")

    def stop(self):

        if self.scheduler.running:
            self.scheduler.shutdown(
                wait=False
            )

        print("Scheduler parado.")

    def check_alarms(self):
        now = datetime.now()

        current_time = now.strftime("%H:%M")
        current_day = now.weekday()

        alarms = get_all_alarms()

        for alarm in alarms:

            # Alarme desativado
            if not alarm["ativo"]:
                continue

            # Horário diferente
            if alarm["horario"] != current_time:
                continue

            # Verifica o dia da semana
            days = get_alarm_days(
                alarm["id"]
            )

            if current_day not in days:
                continue

            # Identificador único dessa execução
            execution_key = (
                f"{now.strftime('%Y-%m-%d')}_"
                f"{alarm['id']}_"
                f"{current_time}"
            )

            # Já executou esse alarme neste minuto
            if execution_key in self.executed_alarms:
                continue

            # Marca ANTES de reproduzir
            self.executed_alarms.add(
                execution_key
            )

            print(
                f"Executando alarme: "
                f"{alarm['nome']} "
                f"({alarm['horario']})"
            )

            self.play_alarm(
                alarm["audio_id"]
            )

    def get_audio_path(self, audio_path):
        base_dir = Path(
            __file__
        ).resolve().parents[2]

        return str(
            base_dir / audio_path
        )

    def play_alarm(self, audio_id):

        audio = get_audio( audio_id )

        if not audio:
            print( f"Áudio {audio_id} não encontrado.")
            return

        try:

            clip = AudioProcessor.create_clip(
                file_path=self.get_audio_path( audio["arquivo"]),
                start=audio["inicio"],
                duration=audio["duracao"],
                fade_in=audio["fade_in"],
                fade_out=audio["fade_out"]
            )

            AudioProcessor.play_clip( clip )

        except Exception as error:

            print( f"Erro ao reproduzir áudio: {error}")

