/**
 * Name: sounds.js
 * Description: Sound effects utility for the Minesweeper game
 * Inputs: None
 * Outputs: Sound playback functions
 * External Sources: Web Audio API
 * Author(s): AI Assistant
 * Creation Date: 2 October 2025
 */

class SoundManager {
  constructor() {
    this.audioContext = null;
    this.enabled = true;
  }

  /**
   * Initialize the audio context (must be called after user interaction)
   */
  init() {
    if (!this.audioContext) {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    return this.audioContext;
  }

  /**
   * Play a simple tone
   * @param {number} frequency - Frequency in Hz
   * @param {number} duration - Duration in milliseconds
   * @param {string} type - Waveform type ('sine', 'square', 'sawtooth', 'triangle')
   */
  playTone(frequency, duration, type = 'sine') {
    if (!this.enabled) return;
    
    const ctx = this.init();
    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();

    oscillator.type = type;
    oscillator.frequency.value = frequency;
    
    gainNode.gain.setValueAtTime(0.3, ctx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration / 1000);

    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);

    oscillator.start(ctx.currentTime);
    oscillator.stop(ctx.currentTime + duration / 1000);
  }

  /**
   * Play multiple tones in sequence
   * @param {Array} notes - Array of {frequency, duration, type} objects
   */
  playSequence(notes) {
    if (!this.enabled) return;
    
    let totalDelay = 0;
    notes.forEach(note => {
      setTimeout(() => {
        this.playTone(note.frequency, note.duration, note.type);
      }, totalDelay);
      totalDelay += note.duration;
    });
  }

  /**
   * Play win sound - uplifting ascending melody
   */
  playWin() {
    const winMelody = [
      { frequency: 523.25, duration: 150, type: 'sine' }, // C5
      { frequency: 659.25, duration: 150, type: 'sine' }, // E5
      { frequency: 783.99, duration: 150, type: 'sine' }, // G5
      { frequency: 1046.50, duration: 300, type: 'sine' } // C6
    ];
    this.playSequence(winMelody);
  }

  /**
   * Play lose sound - descending "sad" melody
   */
  playLose() {
    const loseMelody = [
      { frequency: 523.25, duration: 150, type: 'sine' }, // C5
      { frequency: 493.88, duration: 150, type: 'sine' }, // B4
      { frequency: 440.00, duration: 150, type: 'sine' }, // A4
      { frequency: 392.00, duration: 400, type: 'sine' }  // G4
    ];
    this.playSequence(loseMelody);
  }

  /**
   * Play bomb explosion sound - harsh dramatic sound
   */
  playBomb() {
    if (!this.enabled) return;
    
    const ctx = this.init();
    
    // Create a more complex bomb sound with noise and low frequency rumble
    const duration = 0.5;
    
    // Low frequency rumble
    const oscillator1 = ctx.createOscillator();
    oscillator1.type = 'sawtooth';
    oscillator1.frequency.value = 50;
    
    const gainNode1 = ctx.createGain();
    gainNode1.gain.setValueAtTime(0.4, ctx.currentTime);
    gainNode1.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration);
    
    oscillator1.connect(gainNode1);
    gainNode1.connect(ctx.destination);
    
    // High frequency "crack"
    const oscillator2 = ctx.createOscillator();
    oscillator2.type = 'square';
    oscillator2.frequency.value = 200;
    
    const gainNode2 = ctx.createGain();
    gainNode2.gain.setValueAtTime(0.3, ctx.currentTime);
    gainNode2.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1);
    
    oscillator2.connect(gainNode2);
    gainNode2.connect(ctx.destination);
    
    // Start and stop
    const now = ctx.currentTime;
    oscillator1.start(now);
    oscillator1.stop(now + duration);
    oscillator2.start(now);
    oscillator2.stop(now + 0.1);
  }

  /**
   * Toggle sound on/off
   */
  toggle() {
    this.enabled = !this.enabled;
    return this.enabled;
  }

  /**
   * Set sound enabled state
   * @param {boolean} enabled
   */
  setEnabled(enabled) {
    this.enabled = enabled;
  }
}

// Export singleton instance
export const soundManager = new SoundManager();

