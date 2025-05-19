import AudioService from './AudioService';

const RT_WS_URL = `ws://${window.location.hostname}:8000/ws/realtime`;

class RealTimeService {
  private static instance: RealTimeService;
  private ws: WebSocket | null = null;
  private audioService = AudioService.getInstance();

  public static getInstance(): RealTimeService {
    if (!RealTimeService.instance) {
      RealTimeService.instance = new RealTimeService();
    }
    return RealTimeService.instance;
  }

  public connect() {
    if (this.ws) return;
    this.ws = new WebSocket(RT_WS_URL);
    this.ws.binaryType = 'arraybuffer';
  }

  public disconnect() {
    this.ws?.close();
    this.ws = null;
  }

  public sendAudioChunk(chunk: ArrayBuffer) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(chunk);
    }
  }

  /**
   * Starts recording audio and streams raw chunks to the realtime websocket.
   * This is a simplified implementation and may need adaptation to match the
   * backend protocol once fully defined.
   */
  public async startStreaming() {
    this.connect();
    await this.audioService.startRecording((blob) => {
      // onStop callback; send final chunk
      blob.arrayBuffer().then((buf) => this.sendAudioChunk(buf));
    });
  }

  public stopStreaming() {
    this.audioService.stopRecording();
  }
}

export default RealTimeService;
