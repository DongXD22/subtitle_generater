from pathlib import Path
from utils import *


# WHISPER_PATH = HOME_PATH/'whisper.cpp'/'build_cuda'/'bin'/'whisper-cli.exe'
# GGML_LARGE_PATH = HOME_PATH/'whisper.cpp'/'models'/'ggml-large-v3.bin'
# GGML_MEDIUM_PATH = HOME_PATH/'whisper.cpp'/'models'/'ggml-medium.bin'
# VAD_MODEL_PATH = HOME_PATH/'ggml-silero-v5.1.2.bin'
# GGML_PATH = GGML_LARGE_PATH


class Whisper:

    def __init__(self, whisper_cpp_path: Path, ggml_path: Path) -> None:
        self.whisper_cpp_path = whisper_cpp_path
        self.ggml_path = ggml_path

    def generate_subtitle_raw(self, file_path: Path, lang: str = 'zh', trans_to: str = 'None', ggml_prompt: str = ''):

        ggml_prompt_ = ""
        if lang == 'zh':
            ggml_prompt_ = "以下是简体中文的语音生成文字，"+ggml_prompt

        output_path = STORAGE_PATH/"subtitles_raw"/file_path.stem

        command = [
            str(self.whisper_cpp_path),
            "-m", str(self.ggml_path),
            "-f", str(file_path).strip(),
            "-osrt",
            "-l", lang,
            "--prompt", ggml_prompt_,
            "-of", str(output_path),
            "-ml", "80"
        ]

        command = [arg.strip() for arg in command]
        if run_command(command, __name__):
            print(f"成功导出{file_path.name}的字幕：{output_path}")

        else:
            print(f"导出{file_path.name}字幕失败")
            return None

# region 废案

    # def generate_subtitle_auto(self, task: dict):
    #     """
    #     自动处理切分音频：批量识别 + 合并字幕（自动时间补偿）
    #     """
    #     lang = task["lang"]
    #     trans_to = task["trans_to"]
    #     ggml_prompt = task["ggml_prompt"]

    #     # 切分后音频目录
    #     split_dir = STORAGE_PATH/"audio_split"
    #     srt_output_dir = Path(get_path_by_folder_name("subtitles_raw", task))

    #     # 找出所有分段音频
    #     audio_files = sorted(split_dir.glob("part_*.wav"))
    #     if not audio_files:
    #         print("❌ 未找到分段音频，请先运行切分。")
    #         return

    #     print(f"📁 检测到 {len(audio_files)} 个分段音频。")
    #     merged_srt_path = STORAGE_PATH/"subtitles_raw"

    #     # 临时保存每段字幕
    #     srt_files = []
    #     for i, audio in enumerate(audio_files):
    #         srt = self.generate_subtitle_raw(
    #             audio, lang, trans_to, ggml_prompt)
    #         srt_files.append(srt)

    #     # 合并并调整时间
    #     self._merge_srt_files(srt_files, merged_srt_path,
    #                           segment_seconds=20*60)
    #     print(f"🎬 已生成合并字幕：{merged_srt_path}")

        # if trans_to=="None":
        #     return

        # command_en=command_raw+[
        #     "-p",ggml_prompt,
        #     "-of",str(output_path_en),
        #     "--task","translate"
        # ]

        # if lang=="en":
        #     shutil.copy(output_path,output_path_en)
        #     return

        # if run_command(command_en,__name__):
        #     print(f"成功导出{file_path.name}的英文字幕：{output_path_en}")

        # else:
        #     print(f"导出{file_path.name}英文字幕失败")
# endregion


if __name__ == "__main__":
    whisper = Whisper()
    file_path = STORAGE_PATH/'audios'/'高等数学A（下）_中国大学MOOC(慕课).wav'
    whisper.generate_subtitle_raw(file_path, 'zh', 'None', '')
