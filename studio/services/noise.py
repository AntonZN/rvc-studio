from df.enhance import enhance, init_df, load_audio, save_audio
from cfg import get_settings

settings = get_settings()


def denoise(record_id, audio_path):
    denoised_file_path = f"{settings.OUTPUT_FOLDER}/{record_id}/denoised.mp3"
    model, df_state, _ = init_df()
    audio, _ = load_audio(audio_path, sr=df_state.sr())
    enhanced = enhance(model, df_state, audio)
    save_audio(denoised_file_path, enhanced, df_state.sr())

    return denoised_file_path
