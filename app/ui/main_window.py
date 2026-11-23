import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from app.audio.processor import AudioProcessor
import shutil
import uuid
from datetime import datetime
from app.audio.processor import AudioProcessor
from app.database.database import (
    insert_audio,
    get_all_audios,
    get_audio,
    update_audio,
    delete_audio,
    insert_alarm,
    get_all_alarms,
    get_alarm_days,
    get_alarm,
    update_alarm,
    delete_alarm,
    set_alarm_active
)

class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Sistema de Alarmes")
        self.geometry("1000x650")
        self.minsize(1500, 600)

        self.selected_audio = None
        self.audio_duration = 0
        self.editing_audio_id = None
        self.editing_alarm_id = None

        self._configure_theme()
        self._create_interface()

    def _configure_theme(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

    def _create_interface(self):

        # =========================
        # CABEÇALHO
        # =========================

        self.header = ctk.CTkFrame(
            self,
            height=70,
            corner_radius=0
        )

        self.header.pack(
            fill="x",
            side="top"
        )

        self.header.pack_propagate(False)

        self.title_label = ctk.CTkLabel(
            self.header,
            text="Sistema de Alarmes",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        self.title_label.pack(
            side="left",
            padx=25
        )

        # =========================
        # MENU
        # =========================

        self.menu = ctk.CTkFrame(
            self,
            width=180,
            corner_radius=0
        )

        self.menu.pack(
            fill="y",
            side="left"
        )

        self.menu.pack_propagate(False)

        self.btn_alarm = ctk.CTkButton(
            self.menu,
            text="⏰  Alarmes",
            height=45,
            command=self.show_alarms
        )

        self.btn_alarm.pack(
            padx=15,
            pady=(25, 10),
            fill="x"
        )

        self.btn_audio = ctk.CTkButton(
            self.menu,
            text="🎵  Áudios",
            height=45,
            command=self.show_audios
        )

        self.btn_audio.pack(
            padx=15,
            pady=10,
            fill="x"
        )

        self.btn_settings = ctk.CTkButton(
            self.menu,
            text="⚙  Configurações",
            height=45,
            command=self.show_settings
        )

        self.btn_settings.pack(
            padx=15,
            pady=10,
            fill="x"
        )

        # =========================
        # CONTEÚDO
        # =========================

        self.content = ctk.CTkFrame(
            self,
            corner_radius=0
        )

        self.content.pack(
            fill="both",
            expand=True,
            side="right"
        )

        self.show_alarms()

    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()

    def format_time(self, seconds: float) -> str:
        seconds = int(seconds)

        minutes = seconds // 60
        seconds = seconds % 60

        return f"{minutes:02d}:{seconds:02d}"

    def show_alarms(self):
        self.clear_content()

        title = ctk.CTkLabel(
            self.content,
            text="Alarmes",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        )

        title.pack(
            anchor="w",
            padx=30,
            pady=(30, 5)
        )

        description = ctk.CTkLabel(
            self.content,
            text="Gerencie os horários programados para reprodução."
        )

        description.pack(
            anchor="w",
            padx=30
        )

        # =========================
        # BOTÃO ADICIONAR
        # =========================

        add_button = ctk.CTkButton(
            self.content,
            text="+  Adicionar alarme",
            width=170,
            command=self.show_alarm_editor
        )

        add_button.pack(
            anchor="e",
            padx=30,
            pady=(20, 10)
        )

        # =========================
        # LISTA
        # =========================

        self.alarm_list_frame = ctk.CTkScrollableFrame(
            self.content
        )

        self.alarm_list_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(5, 30)
        )

        self.load_alarm_list()

    def show_alarm_editor(self, alarm_id=None):
        self.clear_content()

        self.editing_alarm_id = alarm_id

        title_text = (
            "Editar alarme"
            if alarm_id
            else "Adicionar alarme"
        )

        title = ctk.CTkLabel(
            self.content,
            text=title_text,
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        )

        title.pack(
            anchor="w",
            padx=30,
            pady=(30, 5)
        )

        description = ctk.CTkLabel(
            self.content,
            text="Configure o horário, os dias e o áudio."
        )

        description.pack(
            anchor="w",
            padx=30
        )

        # =========================
        # FORMULÁRIO
        # =========================

        form = ctk.CTkFrame(
            self.content
        )

        form.pack(
            fill="x",
            padx=30,
            pady=25
        )

        # =========================
        # NOME
        # =========================

        ctk.CTkLabel(
            form,
            text="Nome do alarme:"
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 5)
        )

        self.alarm_name_entry = ctk.CTkEntry(
            form,
            placeholder_text="Ex.: Entrada, Recreio, Saída..."
        )

        self.alarm_name_entry.pack(
            fill="x",
            padx=20
        )

        # =========================
        # HORÁRIO
        # =========================

        ctk.CTkLabel(
            form,
            text="Horário:"
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 5)
        )

        self.alarm_time_entry = ctk.CTkEntry(
            form,
            width=120
        )

        self.alarm_time_entry.insert(
            0,
            "07:00"
        )

        self.alarm_time_entry.pack(
            anchor="w",
            padx=20
        )

        # =========================
        # DIAS
        # =========================

        ctk.CTkLabel(
            form,
            text="Dias da semana:"
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 5)
        )

        days_frame = ctk.CTkFrame(
            form,
            fg_color="transparent"
        )

        days_frame.pack(
            fill="x",
            padx=20
        )

        self.day_vars = {}

        days = [
            (0, "Seg"),
            (1, "Ter"),
            (2, "Qua"),
            (3, "Qui"),
            (4, "Sex"),
            (5, "Sáb"),
            (6, "Dom")
        ]

        for day_id, day_name in days:

            var = ctk.BooleanVar(
                value=False
            )

            checkbox = ctk.CTkCheckBox(
                days_frame,
                text=day_name,
                variable=var
            )

            checkbox.pack(
                side="left",
                padx=(0, 15)
            )

            self.day_vars[day_id] = var

        # =========================
        # ÁUDIO
        # =========================

        ctk.CTkLabel(
            form,
            text="Áudio:"
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 5)
        )

        audios = get_all_audios()

        self.audio_options = {}

        if audios:

            audio_names = [
                audio["nome"]
                for audio in audios
            ]

            for audio in audios:
                self.audio_options[audio["nome"]] = audio["id"]

            self.audio_combobox = ctk.CTkComboBox(
                form,
                values=audio_names,
                width=300
            )

            self.audio_combobox.pack(
                anchor="w",
                padx=20
            )

        else:

            self.audio_combobox = None

            ctk.CTkLabel(
                form,
                text="Nenhum áudio cadastrado. "
                    "Cadastre um áudio primeiro."
            ).pack(
                anchor="w",
                padx=20
            )

        # =========================
        # BOTÕES
        # =========================

        button_frame = ctk.CTkFrame(
            form,
            fg_color="transparent"
        )

        button_frame.pack(
            fill="x",
            padx=20,
            pady=25
        )

        ctk.CTkButton(
            button_frame,
            text="Salvar alarme",
            command=self.save_alarm
        ).pack(
            side="left"
        )

        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            fg_color="gray",
            hover_color="gray",
            command=self.show_alarms
        ).pack(
            side="right"
        )

        # =========================
        # CARREGAR EDIÇÃO
        # =========================

        if alarm_id:
            self.load_alarm_into_editor(alarm_id)

    def load_alarm_list(self):
        for widget in self.alarm_list_frame.winfo_children():
            widget.destroy()

        alarms = get_all_alarms()

        if not alarms:
            ctk.CTkLabel(
                self.alarm_list_frame,
                text="Nenhum alarme cadastrado."
            ).pack(
                pady=30
            )
            return

        day_names = [
            "Seg",
            "Ter",
            "Qua",
            "Qui",
            "Sex",
            "Sáb",
            "Dom"
        ]

        for alarm in alarms:

            card = ctk.CTkFrame(
                self.alarm_list_frame
            )

            card.pack(
                fill="x",
                pady=6,
                padx=5
            )

            # =========================
            # INFORMAÇÕES
            # =========================

            info_frame = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )

            info_frame.pack(
                side="left",
                fill="x",
                expand=True,
                padx=15,
                pady=12
            )

            name_label = ctk.CTkLabel(
                info_frame,
                text=alarm["nome"],
                font=ctk.CTkFont(
                    size=17,
                    weight="bold"
                )
            )

            name_label.pack(
                anchor="w"
            )

            days = get_alarm_days(alarm["id"])

            days_text = " ".join(
                day_names[day]
                for day in days
            )

            details = ctk.CTkLabel(
                info_frame,
                text=(
                    f"Horário: {alarm['horario']}   |   "
                    f"Dias: {days_text}   |   "
                    f"Áudio: {alarm['audio_nome']}"
                )
            )

            details.pack(
                anchor="w",
                pady=(4, 0)
            )

            # =========================
            # STATUS
            # =========================

            status_text = (
                "Ativo"
                if alarm["ativo"]
                else "Desativado"
            )

            status_button = ctk.CTkButton(
                card,
                text=status_text,
                width=100
            )

            status_button.configure(
                command=lambda
                    alarm_id=alarm["id"],
                    status=alarm["ativo"],
                    button=status_button:
                        self.toggle_alarm(
                            alarm_id,
                            status,
                            button
                        )
            )

            status_button.pack(
                side="left",
                padx=10
            )

            # =========================
            # EDITAR
            # =========================

            edit_button = ctk.CTkButton(
                card,
                text="Editar",
                width=80,
                command=lambda alarm_id=alarm["id"]:
                    self.show_alarm_editor(alarm_id)
            )

            edit_button.pack(
                side="right",
                padx=(5, 15),
                pady=15
            )

            # =========================
            # EXCLUIR
            # =========================

            delete_button = ctk.CTkButton(
                card,
                text="Excluir",
                width=80,
                fg_color="#8B0000",
                hover_color="#A00000",
                command=lambda alarm_id=alarm["id"]:
                    self.confirm_delete_alarm(alarm_id)
            )

            delete_button.pack(
                side="right",
                padx=5,
                pady=15
            )

    def confirm_delete_alarm(self, alarm_id):
        confirmation = messagebox.askyesno(
            "Excluir alarme",
            "Tem certeza que deseja excluir este alarme?"
        )

        if not confirmation:
            return

        try:

            delete_alarm(alarm_id)

            messagebox.showinfo(
                "Alarme excluído",
                "O alarme foi excluído com sucesso."
            )

            self.show_alarms()

        except Exception as error:

            messagebox.showerror(
                "Erro",
                f"Não foi possível excluir o alarme.\n\n{error}"
            )

    def save_alarm(self):
        try:

            horario = self.alarm_time_entry.get().strip()

            try:
                datetime.strptime(
                    horario,
                    "%H:%M"
                )
            except ValueError:
                raise ValueError(
                    "O horário deve estar no formato HH:MM.\n"
                    "Exemplo: 07:30"
                )

            selected_days = [
                day_id
                for day_id, var in self.day_vars.items()
                if var.get()
            ]

            if not selected_days:
                raise ValueError(
                    "Selecione pelo menos um dia da semana."
                )

            if not self.audio_combobox:

                raise ValueError(
                    "Cadastre pelo menos um áudio antes "
                    "de criar um alarme."
                )

            selected_audio_name = (
                self.audio_combobox.get()
            )

            audio_id = self.audio_options.get(
                selected_audio_name
            )

            if not audio_id:
                raise ValueError(
                    "Selecione um áudio."
                )

            nome = (
                self.alarm_name_entry
                .get()
                .strip()
            )

            if not nome:
                nome = f"Alarme {horario}"

            if not self.editing_alarm_id:

                insert_alarm(
                    nome=nome,
                    horario=horario,
                    audio_id=audio_id,
                    dias=selected_days
                )

                messagebox.showinfo(
                    "Alarme salvo",
                    "O alarme foi cadastrado com sucesso."
                )

            else:

                update_alarm(
                    alarm_id=self.editing_alarm_id,
                    nome=nome,
                    horario=horario,
                    audio_id=audio_id,
                    dias=selected_days
                )

                messagebox.showinfo(
                    "Alarme atualizado",
                    "O alarme foi atualizado com sucesso."
                )

            self.show_alarms()

        except ValueError as error:

            messagebox.showerror(
                "Valor inválido",
                str(error)
            )

        except Exception as error:

            messagebox.showerror(
                "Erro",
                f"Não foi possível salvar o alarme.\n\n{error}"
            )

    def show_audios(self):

        self.clear_content()

        title = ctk.CTkLabel(
            self.content,
            text="Áudios",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        )

        title.pack(
            anchor="w",
            padx=30,
            pady=(30, 5)
        )

        description = ctk.CTkLabel(
            self.content,
            text="Gerencie os áudios utilizados pelo sistema."
        )

        description.pack(
            anchor="w",
            padx=30
        )

        # =========================
        # BOTÃO ADICIONAR
        # =========================

        add_button = ctk.CTkButton(
            self.content,
            text="+  Adicionar áudio",
            width=160,
            command=self.show_audio_editor
        )

        add_button.pack(
            anchor="e",
            padx=30,
            pady=(20, 10)
        )

        # =========================
        # LISTA
        # =========================

        self.audio_list_frame = ctk.CTkScrollableFrame(
            self.content
        )

        self.audio_list_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(5, 30)
        )

        self.load_audio_list()

    def show_audio_editor(self, audio_id=None):
        self.clear_content()

        self.editing_audio_id = audio_id

        title_text = (
            "Editar áudio"
            if audio_id
            else "Adicionar áudio"
        )

        title = ctk.CTkLabel(
            self.content,
            text=title_text,
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        )

        title.pack(
            anchor="w",
            padx=30,
            pady=(30, 5)
        )

        description = ctk.CTkLabel(
            self.content,
            text="Configure o trecho que será reproduzido."
        )

        description.pack(
            anchor="w",
            padx=30
        )

        # =========================
        # ARQUIVO
        # =========================

        file_frame = ctk.CTkFrame(
            self.content
        )

        file_frame.pack(
            fill="x",
            padx=30,
            pady=25
        )

        self.file_label = ctk.CTkLabel(
            file_frame,
            text="Nenhum áudio selecionado",
            anchor="w"
        )

        self.file_label.pack(
            side="left",
            padx=15,
            pady=15,
            fill="x",
            expand=True
        )

        select_button = ctk.CTkButton(
            file_frame,
            text="Selecionar áudio",
            command=self.select_audio
        )

        select_button.pack(
            side="right",
            padx=15,
            pady=15
        )

        # =========================
        # EDITOR
        # =========================

        self.editor_frame = ctk.CTkFrame(
            self.content
        )

        self.editor_frame.pack(
            fill="x",
            padx=30,
            pady=10
        )

        self.create_audio_editor()

        # =========================
        # CARREGAR EDIÇÃO
        # =========================

        if audio_id:

            audio = get_audio(audio_id)

            if audio:

                self.selected_audio = str(
                    Path(
                        Path(__file__).resolve().parents[2]
                        / audio["arquivo"]
                    )
                )

                self.audio_duration = (
                    AudioProcessor.get_duration(
                        self.selected_audio
                    )
                )

                self.file_label.configure(
                    text=audio["nome"]
                )

                self.duration_label.configure(
                    text=(
                        "Duração do áudio: "
                        f"{self.format_time(self.audio_duration)}"
                    )
                )

                self.start_entry.delete(
                    0,
                    "end"
                )

                self.start_entry.insert(
                    0,
                    self.format_time(audio["inicio"])
                )

                self.clip_duration_entry.delete(
                    0,
                    "end"
                )

                self.clip_duration_entry.insert(
                    0,
                    self.format_time(audio["duracao"])
                )

                self.fade_in_entry.delete(
                    0,
                    "end"
                )

                self.fade_in_entry.insert(
                    0,
                    str(audio["fade_in"])
                )

                self.fade_out_entry.delete(
                    0,
                    "end"
                )

                self.fade_out_entry.insert(
                    0,
                    str(audio["fade_out"])
                )

    def select_audio(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar áudio",
            filetypes=[
                (
                    "Arquivos de áudio",
                    "*.mp3 *.wav *.ogg *.flac *.m4a"
                ),
                (
                    "Todos os arquivos",
                    "*.*"
                )
            ]
        )

        if not file_path:
            return

        try:

            duration = AudioProcessor.get_duration(file_path)

            self.selected_audio = file_path
            self.audio_duration = duration

            # Mostrar somente o nome do arquivo
            file_name = Path(file_path).name

            self.file_label.configure(
                text=file_name
            )

            self.duration_label.configure(
                text=f"Duração do áudio: {self.format_time(duration)}"
            )

        except Exception as error:

            messagebox.showerror(
                "Erro",
                f"Não foi possível carregar o áudio.\n\n{error}"
            )

    def create_audio_editor(self):

        title = ctk.CTkLabel(
            self.editor_frame,
            text="Configuração do trecho",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        )

        title.pack(
            anchor="w",
            padx=20,
            pady=(20, 15)
        )

        # =========================
        # DURAÇÃO DO ÁUDIO
        # =========================

        self.duration_label = ctk.CTkLabel(
            self.editor_frame,
            text="Duração do áudio: --"
        )

        self.duration_label.pack(
            anchor="w",
            padx=20
        )

        # =========================
        # INÍCIO
        # =========================

        start_frame = ctk.CTkFrame(
            self.editor_frame,
            fg_color="transparent"
        )

        start_frame.pack(
            fill="x",
            padx=20,
            pady=(20, 10)
        )

        ctk.CTkLabel(
            start_frame,
            text="Início do trecho (segundos):"
        ).pack(
            side="left"
        )

        self.start_entry = ctk.CTkEntry(
            start_frame,
            width=120
        )

        self.start_entry.insert(0, "00:00")

        self.start_entry.pack( side="right" )

        # =========================
        # DURAÇÃO
        # =========================

        duration_frame = ctk.CTkFrame(
            self.editor_frame,
            fg_color="transparent"
        )

        duration_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        ctk.CTkLabel(
            duration_frame,
            text="Duração do trecho (segundos):"
        ).pack(
            side="left"
        )

        self.clip_duration_entry = ctk.CTkEntry(
            duration_frame,
            width=120
        )

        self.clip_duration_entry.insert(0, "00:15")

        self.clip_duration_entry.pack( side="right" )

        # =========================
        # FADE IN
        # =========================

        fade_in_frame = ctk.CTkFrame(
            self.editor_frame,
            fg_color="transparent"
        )

        fade_in_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        ctk.CTkLabel(
            fade_in_frame,
            text="Fade In (segundos):"
        ).pack(
            side="left"
        )

        self.fade_in_entry = ctk.CTkEntry(
            fade_in_frame,
            width=120
        )

        self.fade_in_entry.insert(
            0,
            "1"
        )

        self.fade_in_entry.pack(
            side="right"
        )

        # =========================
        # FADE OUT
        # =========================

        fade_out_frame = ctk.CTkFrame(
            self.editor_frame,
            fg_color="transparent"
        )

        fade_out_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        ctk.CTkLabel(
            fade_out_frame,
            text="Fade Out (segundos):"
        ).pack(
            side="left"
        )

        self.fade_out_entry = ctk.CTkEntry(
            fade_out_frame,
            width=120
        )

        self.fade_out_entry.insert(
            0,
            "1"
        )

        self.fade_out_entry.pack(
            side="right"
        )

        # =========================
        # BOTÕES
        # =========================

        button_frame = ctk.CTkFrame(
            self.editor_frame,
            fg_color="transparent"
        )

        button_frame.pack(
            fill="x",
            padx=20,
            pady=20
        )

        self.test_button = ctk.CTkButton(
            button_frame,
            text="▶  Testar trecho",
            command=self.test_clip
        )

        self.test_button.pack(
            side="left"
        )

        self.save_button = ctk.CTkButton(
            button_frame,
            text="Salvar áudio",
            command=self.save_audio
        )

        self.save_button.pack(
            side="right"
        )

    def load_audio_list(self):
        for widget in self.audio_list_frame.winfo_children():
            widget.destroy()

        audios = get_all_audios()

        if not audios:

            label = ctk.CTkLabel(
                self.audio_list_frame,
                text="Nenhum áudio cadastrado.",
                font=ctk.CTkFont(
                    size=16
                )
            )

            label.pack(
                pady=40
            )

            return

        for audio in audios:

            self.create_audio_card(audio)

    def create_audio_card(self, audio):
        card = ctk.CTkFrame(
            self.audio_list_frame
        )

        card.pack(
            fill="x",
            pady=6
        )

        # =========================
        # INFORMAÇÕES
        # =========================

        info_frame = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        info_frame.pack(
            side="left",
            fill="x",
            expand=True,
            padx=15,
            pady=12
        )

        name_label = ctk.CTkLabel(
            info_frame,
            text=f"🔊  {audio['nome']}",
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            ),
            anchor="w"
        )

        name_label.pack(
            anchor="w"
        )

        start = self.format_time(
            audio["inicio"]
        )

        end = self.format_time(
            audio["inicio"] + audio["duracao"]
        )

        details_label = ctk.CTkLabel(
            info_frame,
            text=f"Trecho: {start} → {end}",
            anchor="w"
        )

        details_label.pack(
            anchor="w",
            pady=(3, 0)
        )

        # =========================
        # BOTÕES
        # =========================

        button_frame = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        button_frame.pack(
            side="right",
            padx=15,
            pady=12
        )

        edit_button = ctk.CTkButton(
            button_frame,
            text="Editar",
            width=80,
            command=lambda audio_id=audio["id"]:
                self.show_audio_editor(audio_id)
        )

        edit_button.pack(
            side="left",
            padx=5
        )

        delete_button = ctk.CTkButton(
            button_frame,
            text="Excluir",
            width=80,
            fg_color="#B91C1C",
            hover_color="#991B1B",
            command=lambda audio_id=audio["id"]:
                self.confirm_delete_audio(audio_id)
        )

        delete_button.pack(
            side="left",
            padx=5
        )

    def confirm_delete_audio(self, audio_id):
        audio = get_audio(audio_id)

        if not audio:
            return

        confirm = messagebox.askyesno(
            "Excluir áudio",
            (
                f"Tem certeza que deseja excluir "
                f"'{audio['nome']}'?\n\n"
                "O arquivo local também será excluído."
            )
        )

        if not confirm:
            return

        try:

            base_dir = Path(
                __file__
            ).resolve().parents[2]

            audio_path = (
                base_dir / audio["arquivo"]
            )

            delete_audio(audio_id)

            if audio_path.exists():
                audio_path.unlink()

            messagebox.showinfo(
                "Áudio excluído",
                "O áudio foi excluído com sucesso."
            )

            self.show_audios()

        except ValueError as error:

            messagebox.showwarning(
                "Não é possível excluir",
                str(error)
            )

        except Exception as error:

            messagebox.showerror(
                "Erro",
                f"Não foi possível excluir o áudio.\n\n{error}"
            )

    def test_clip(self):
        if not self.selected_audio:
            messagebox.showwarning(
                "Áudio não selecionado",
                "Selecione um arquivo de áudio primeiro."
            )
            return

        try:
            start = AudioProcessor.parse_time(
                self.start_entry.get()
            )

            duration = AudioProcessor.parse_time(
                self.clip_duration_entry.get()
            )

            fade_in = float(
                self.fade_in_entry.get()
            )

            fade_out = float(
                self.fade_out_entry.get()
            )

            clip = AudioProcessor.create_clip(
                file_path=self.selected_audio,
                start=start,
                duration=duration,
                fade_in=fade_in,
                fade_out=fade_out
            )

            AudioProcessor.play_clip(clip)

        except ValueError as error:

            messagebox.showerror(
                "Valor inválido",
                str(error)
            )

        except Exception as error:

            messagebox.showerror(
                "Erro",
                f"Não foi possível processar o áudio.\n\n{error}"
            )

    def save_audio(self):
        if not self.selected_audio:
            messagebox.showwarning(
                "Áudio não selecionado",
                "Selecione um arquivo de áudio primeiro."
            )
            return

        try:
            start = AudioProcessor.parse_time(
                self.start_entry.get()
            )

            duration = AudioProcessor.parse_time(
                self.clip_duration_entry.get()
            )

            fade_in = float(
                self.fade_in_entry.get()
            )

            fade_out = float(
                self.fade_out_entry.get()
            )

            # Valida o trecho
            AudioProcessor.create_clip(
                file_path=self.selected_audio,
                start=start,
                duration=duration,
                fade_in=fade_in,
                fade_out=fade_out
            )

            base_dir = Path(
                __file__
            ).resolve().parents[2]

            audios_dir = base_dir / "audios"

            audios_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            original_path = Path(
                self.selected_audio
            )

            # =================================
            # NOVO ÁUDIO
            # =================================

            if not self.editing_audio_id:

                extension = original_path.suffix

                unique_name = (
                    f"{uuid.uuid4().hex}{extension}"
                )

                destination = (
                    audios_dir / unique_name
                )

                shutil.copy2(
                    original_path,
                    destination
                )

                insert_audio(
                    nome=original_path.name,
                    arquivo=str(
                        Path("audios") / unique_name
                    ),
                    inicio=start,
                    duracao=duration,
                    fade_in=fade_in,
                    fade_out=fade_out
                )

                messagebox.showinfo(
                    "Áudio salvo",
                    "O áudio foi cadastrado com sucesso."
                )

            # =================================
            # EDIÇÃO
            # =================================

            else:

                current_audio = get_audio(
                    self.editing_audio_id
                )

                if not current_audio:
                    raise ValueError(
                        "O áudio não foi encontrado no banco."
                    )

                current_path = (
                    base_dir / current_audio["arquivo"]
                )

                # Verifica se o usuário trocou o arquivo
                current_resolved = (
                    current_path.resolve()
                    if current_path.exists()
                    else None
                )

                selected_resolved = (
                    original_path.resolve()
                )

                file_changed = (
                    current_resolved != selected_resolved
                )

                if file_changed:

                    extension = original_path.suffix

                    unique_name = (
                        f"{uuid.uuid4().hex}{extension}"
                    )

                    destination = (
                        audios_dir / unique_name
                    )

                    shutil.copy2(
                        original_path,
                        destination
                    )

                    new_audio_path = str(
                        Path("audios") / unique_name
                    )

                    update_audio(
                        audio_id=self.editing_audio_id,
                        nome=original_path.name,
                        arquivo=new_audio_path,
                        inicio=start,
                        duracao=duration,
                        fade_in=fade_in,
                        fade_out=fade_out
                    )

                    # Só remove o arquivo antigo depois
                    # que o novo foi copiado e salvo no banco.
                    if (
                        current_path.exists()
                        and current_path.resolve()
                        != destination.resolve()
                    ):
                        current_path.unlink()

                else:

                    update_audio(
                        audio_id=self.editing_audio_id,
                        nome=current_audio["nome"],
                        arquivo=current_audio["arquivo"],
                        inicio=start,
                        duracao=duration,
                        fade_in=fade_in,
                        fade_out=fade_out
                    )

                messagebox.showinfo(
                    "Áudio atualizado",
                    "O áudio foi atualizado com sucesso."
                )

            # Voltar para a lista
            self.show_audios()

        except ValueError as error:

            messagebox.showerror(
                "Valor inválido",
                str(error)
            )

        except Exception as error:

            messagebox.showerror(
                "Erro",
                f"Não foi possível salvar o áudio.\n\n{error}"
            )
    
    def load_alarm_into_editor(self, alarm_id):
        alarm = get_alarm(alarm_id)

        if not alarm:
            messagebox.showerror(
                "Erro",
                "Alarme não encontrado."
            )
            self.show_alarms()
            return

        # =========================
        # NOME
        # =========================

        self.alarm_name_entry.delete(
            0,
            "end"
        )

        self.alarm_name_entry.insert(
            0,
            alarm["nome"] or ""
        )

        # =========================
        # HORÁRIO
        # =========================

        self.alarm_time_entry.delete(
            0,
            "end"
        )

        self.alarm_time_entry.insert(
            0,
            alarm["horario"]
        )

        # =========================
        # DIAS
        # =========================

        selected_days = get_alarm_days(alarm_id)

        for day_id, variable in self.day_vars.items():
            variable.set(
                day_id in selected_days
            )

        # =========================
        # ÁUDIO
        # =========================

        if self.audio_combobox:

            for audio_name, audio_id in self.audio_options.items():

                if audio_id == alarm["audio_id"]:

                    self.audio_combobox.set(
                        audio_name
                    )

                    break
    
    def toggle_alarm(self, alarm_id, current_status, status_button):
        try:

            new_status = not bool(current_status)

            set_alarm_active(
                alarm_id,
                new_status
            )

            status_button.configure(
                text="Ativo" if new_status else "Desativado"
            )

            # Atualiza o comando do botão para manter
            # o novo estado
            status_button.configure(
                command=lambda:
                    self.toggle_alarm(
                        alarm_id,
                        new_status,
                        status_button
                    )
            )

        except Exception as error:

            messagebox.showerror(
                "Erro",
                f"Não foi possível alterar o status do alarme.\n\n{error}"
            )
    
    def show_settings(self):

        self.clear_content()

        title = ctk.CTkLabel(
            self.content,
            text="Configurações",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        )

        title.pack(
            anchor="w",
            padx=30,
            pady=(30, 10)
        )

        description = ctk.CTkLabel(
            self.content,
            text="Configurações do sistema."
        )

        description.pack(
            anchor="w",
            padx=30
        )