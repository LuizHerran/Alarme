from pathlib import Path

import sounddevice as sd
from pydub import AudioSegment


class AudioProcessor:
    
    @staticmethod
    def parse_time(value: str) -> float:
        """
        Converte:
            95      -> 95 segundos
            1:35    -> 95 segundos
            01:35   -> 95 segundos
            1:02:30 -> 3750 segundos
        """
        value = value.strip()

        if not value:
            raise ValueError("Informe um tempo.")

        try:
            if ":" not in value:
                seconds = float(value)

            else:
                parts = value.split(":")

                if len(parts) == 2:
                    minutes = int(parts[0])
                    seconds = float(parts[1])

                    if minutes < 0 or seconds < 0 or seconds >= 60:
                        raise ValueError(
                            "Formato de tempo inválido. Use MM:SS."
                        )

                    seconds = minutes * 60 + seconds

                elif len(parts) == 3:
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    seconds_part = float(parts[2])

                    if (
                        hours < 0
                        or minutes < 0
                        or minutes >= 60
                        or seconds_part < 0
                        or seconds_part >= 60
                    ):
                        raise ValueError(
                            "Formato de tempo inválido. Use HH:MM:SS."
                        )

                    seconds = (
                        hours * 3600
                        + minutes * 60
                        + seconds_part
                    )

                else:
                    raise ValueError(
                        "Formato de tempo inválido. Use MM:SS."
                    )

            if seconds < 0:
                raise ValueError("O tempo não pode ser negativo.")

            return seconds

        except ValueError:
            raise ValueError(
                "Tempo inválido. Use, por exemplo: 1:15"
            )

    @staticmethod
    def get_duration(file_path: str) -> float:
        """
        Retorna a duração do áudio em segundos.
        """

        audio = AudioSegment.from_file(file_path)

        return len(audio) / 1000

    @staticmethod
    def create_clip(
        file_path: str,
        start: float,
        duration: float = 15,
        fade_in: float = 1,
        fade_out: float = 1,
    ) -> AudioSegment:
        """
        Cria um trecho do áudio aplicando fade in e fade out.
        """

        if start < 0:
            raise ValueError(
                "O início não pode ser negativo."
            )

        if duration <= 0:
            raise ValueError(
                "A duração deve ser maior que zero."
            )

        if fade_in < 0 or fade_out < 0:
            raise ValueError(
                "Os fades não podem ser negativos."
            )

        audio = AudioSegment.from_file(file_path)

        start_ms = int(start * 1000)
        duration_ms = int(duration * 1000)
        end_ms = start_ms + duration_ms

        if start_ms >= len(audio):
            raise ValueError(
                "O início está além da duração do áudio."
            )

        clip = audio[start_ms:end_ms]

        if len(clip) == 0:
            raise ValueError(
                "Não foi possível criar o trecho."
            )

        fade_in_ms = min(
            int(fade_in * 1000),
            len(clip) // 2
        )

        fade_out_ms = min(
            int(fade_out * 1000),
            len(clip) // 2
        )

        if fade_in_ms > 0:
            clip = clip.fade_in(fade_in_ms)

        if fade_out_ms > 0:
            clip = clip.fade_out(fade_out_ms)

        return clip

    @staticmethod
    def play_clip(clip: AudioSegment):
        """
        Reproduz um trecho diretamente na saída de áudio
        do sistema, sem criar arquivo.
        """

        samples = clip.get_array_of_samples()

        # O sounddevice espera dados PCM.
        # Convertemos para float entre -1 e 1.
        import numpy as np

        audio_data = np.array(
            samples,
            dtype=np.float32
        )

        max_value = float(
            2 ** (8 * clip.sample_width - 1)
        )

        audio_data /= max_value

        if clip.channels > 1:
            audio_data = audio_data.reshape(
                (-1, clip.channels)
            )

        sd.stop()

        sd.play(
            audio_data,
            samplerate=clip.frame_rate
        )

    @staticmethod
    def stop_playback():
        """
        Para imediatamente a reprodução.
        """

        sd.stop()

    @staticmethod
    def save_clip(
        clip: AudioSegment,
        output_path: str,
        format: str = "mp3",
    ):
        """
        Salva o trecho processado.
        Usado apenas quando realmente quisermos
        criar um arquivo definitivo.
        """

        output = Path(output_path)

        output.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        clip.export(
            output,
            format=format
        )