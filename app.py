from app.database.database import initialize_database
from app.ui.main_window import MainWindow
from app.scheduler.scheduler import AlarmScheduler


def main():

    # Inicializar banco de dados
    initialize_database()

    # Iniciar agendador de alarmes
    scheduler = AlarmScheduler()
    scheduler.start()

    # Iniciar interface gráfica
    app = MainWindow()

    try:
        app.mainloop()

    finally:
        # Encerrar agendador ao fechar a aplicação
        scheduler.stop()


if __name__ == "__main__":
    main()