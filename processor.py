import numpy as np
from scipy.signal import welch

def generate_eeg_stream(state="focus", duration_sec=10, fs=250):
    t = np.linspace(0, duration_sec, duration_sec * fs, endpoint=False)
    
    if state == "focus":
        theta_amp, alpha_amp, beta_amp = 0.5, 0.9, 3.2
    elif state == "fatigued":
        theta_amp, alpha_amp, beta_amp = 3.6, 2.1, 0.5
    else:  # stressed
        theta_amp, alpha_amp, beta_amp = 0.3, 0.5, 4.6

    noise = np.random.normal(0, 0.25, len(t))
    eeg = (
        theta_amp * np.sin(2 * np.pi * 6 * t) +
        alpha_amp * np.sin(2 * np.pi * 10 * t) +
        beta_amp * np.sin(2 * np.pi * 20 * t) +
        noise
    )
    return t, eeg

def extract_band_telemetry(eeg, fs=250):
    freqs, psd = welch(eeg, fs=fs, nperseg=min(len(eeg), 500))
    
    theta = float(np.trapz(psd[(freqs >= 4) & (freqs <= 8)], freqs[(freqs >= 4) & (freqs <= 8)]))
    alpha = float(np.trapz(psd[(freqs >= 8) & (freqs <= 13)], freqs[(freqs >= 8) & (freqs <= 13)]))
    beta = float(np.trapz(psd[(freqs >= 13) & (freqs <= 30)], freqs[(freqs >= 13) & (freqs <= 30)]))
    
    engagement_index = beta / (alpha + theta + 1e-6)
    
    return {
        "theta": round(theta, 3),
        "alpha": round(alpha, 3),
        "beta": round(beta, 3),
        "engagement": round(float(engagement_index), 3)
    }