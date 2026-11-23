import time

from app.database.database import initialize_database
from app.scheduler.scheduler import AlarmScheduler


initialize_database()

scheduler = AlarmScheduler()

scheduler.start()

print("Scheduler rodando.")
print("Pressione CTRL+C para parar.")

try:

    while True:
        time.sleep(1)

except KeyboardInterrupt:

    print("Encerrando...")

    scheduler.stop()