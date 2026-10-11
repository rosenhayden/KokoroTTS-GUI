import asyncio
import flet as ft
import numpy as np
import soundfile as sf
from kokoro import KPipeline

pipeline = KPipeline(lang_code="a")  # load once


def synthesize(text: str, out_path: str) -> str:
    chunks = [audio for _, _, audio in pipeline(
        text, voice="bm_george", speed=1, split_pattern=r"\n+"
    )]
    if not chunks:
        raise ValueError("No audio generated (is the text empty?)")
    sf.write(out_path, np.concatenate(chunks), 24000)
    return out_path


def main(page: ft.Page):
    selected_file_name = ft.Text("No file selected")
    selected_file_content = ft.TextField(
        label="Selected file content", multiline=True, min_lines=8, max_lines=14
    )
    save_status = ft.Text()

    async def pick_text_file(_: ft.Event[ft.Button]):
        files = await ft.FilePicker().pick_files(
            allow_multiple=False,
            with_data=True,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["txt", "md"],
        )
        if not files:
            selected_file_name.value = "Selection cancelled"
            selected_file_content.value = ""
            return
        selected = files[0]
        selected_file_name.value = f"Selected: {selected.name} ({selected.size} bytes)"
        selected_file_content.value = (
            selected.bytes.decode("utf-8", errors="replace") if selected.bytes else ""
        )
        save_status.value = ""

    async def convert_to_audio(_: ft.Event[ft.Button]):
        text = (selected_file_content.value or "").strip()  # .value, not str(control)
        if not text:
            save_status.value = "Nothing to convert"
            return
        save_status.value = "Generating audio..."
        page.update()
        try:
            path = await asyncio.to_thread(synthesize, text, "output.wav")
            save_status.value = f"Saved audio to {path}"
        except Exception as ex:
            save_status.value = f"Error: {ex}"

    page.add(
        ft.SafeArea(
            content=ft.Column(
                controls=[
                    ft.Text("Pick a .txt/.md file, then convert it to speech"),
                    ft.Button(content="Pick text file", icon=ft.Icons.UPLOAD_FILE,
                              on_click=pick_text_file),
                    selected_file_name,
                    selected_file_content,
                    ft.Button(content="Convert to audio", icon=ft.Icons.AUDIOTRACK,
                              on_click=convert_to_audio),
                    save_status,
                ],
            ),
        )
    )


if __name__ == "__main__":
    ft.run(main)
