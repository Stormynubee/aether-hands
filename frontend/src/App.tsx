import { useEffect, useRef, useState } from 'react';
import './App.css';

function App() {
  const [error, setError] = useState<string | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [status, setStatus] = useState('OFFLINE');
  const [lastGesture, setLastGesture] = useState('none');
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    console.log("App mounted - Initializing Aether Hands");
    
    // WebSocket Connection
    const connectWS = () => {
      try {
        const ws = new WebSocket('ws://localhost:8000/ws');
        ws.onopen = () => setStatus('ACTIVE');
        ws.onclose = () => {
          setStatus('OFFLINE');
          setTimeout(connectWS, 3000);
        };
        wsRef.current = ws;
      } catch (e) {
        console.error("WS Error", e);
      }
    };
    connectWS();

    // Vision Initialization
    const initVision = async () => {
      try {
        // @ts-ignore
        const Hands = window.Hands;
        // @ts-ignore
        const Camera = window.Camera;

        if (!Hands || !Camera) {
          console.warn("MediaPipe scripts not found yet, retrying...");
          setTimeout(initVision, 1000);
          return;
        }

        const hands = new Hands({
          locateFile: (file: string) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
        });

        hands.setOptions({
          maxNumHands: 1,
          modelComplexity: 1,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5,
        });

        hands.onResults((results: any) => {
          if (!canvasRef.current) return;
          const ctx = canvasRef.current.getContext('2d');
          if (!ctx) return;

          ctx.save();
          ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
          ctx.translate(canvasRef.current.width, 0);
          ctx.scale(-1, 1);

          if (results.multiHandLandmarks && results.multiHandLandmarks[0]) {
            const landmarks = results.multiHandLandmarks[0];
            
            // @ts-ignore
            const { drawConnectors, drawLandmarks, HAND_CONNECTIONS } = window;
            if (drawConnectors && drawLandmarks && HAND_CONNECTIONS) {
              drawConnectors(ctx, landmarks, HAND_CONNECTIONS, { color: '#00ffff', lineWidth: 2 });
              drawLandmarks(ctx, landmarks, { color: '#ff00ff', radius: 2 });
            }

            // Simple Gesture Detection
            const indexTip = landmarks[8];
            const thumbTip = landmarks[4];
            const dist = Math.hypot(indexTip.x - thumbTip.x, indexTip.y - thumbTip.y);
            const gesture = dist < 0.05 ? 'pinch' : 'point';
            
            setLastGesture(gesture);

            if (wsRef.current?.readyState === 1) {
               wsRef.current.send(JSON.stringify({
                 type: gesture,
                 x: indexTip.x,
                 y: indexTip.y
               }));
            }
          }
          ctx.restore();
        });

        if (videoRef.current) {
          const camera = new Camera(videoRef.current, {
            onFrame: async () => {
              if (videoRef.current) {
                await hands.send({ image: videoRef.current });
              }
            },
            width: 1280,
            height: 720,
          });
          await camera.start();
          console.log("Camera and Hands initialized.");
          setIsLoaded(true);
          setError(null);
        }
      } catch (e: any) {
        console.error("Vision Error:", e);
        setError(e.message || "Failed to start camera.");
      }
    };

    initVision();

    return () => {
      wsRef.current?.close();
    };
  }, []);

  return (
    <div style={{ 
      background: 'black', 
      color: 'white', 
      width: '100vw', 
      height: '100vh', 
      position: 'relative', 
      overflow: 'hidden',
      fontFamily: 'monospace' 
    }}>
      {/* HUD Info */}
      <div style={{ 
        position: 'absolute', 
        top: 30, 
        left: 30, 
        zIndex: 100, 
        borderLeft: '2px solid #00ffff', 
        padding: '10px 20px', 
        background: 'rgba(0,255,255,0.05)',
        backdropFilter: 'blur(5px)'
      }}>
        <div style={{ fontSize: '10px', opacity: 0.5, letterSpacing: '2px' }}>AETHER HUD V1.2</div>
        <div style={{ color: status === 'ACTIVE' ? '#00ffff' : '#ff0055', fontWeight: 'bold' }}>
          SYSTEM: {status}
        </div>
        <div style={{ color: '#ff00ff', fontWeight: 'bold' }}>
          GESTURE: {lastGesture.toUpperCase()}
        </div>
      </div>

      {/* Vision Output */}
      <video ref={videoRef} style={{ display: 'none' }} playsInline muted />
      <canvas 
        ref={canvasRef} 
        width={1280} 
        height={720} 
        style={{ width: '100%', height: '100%', objectFit: 'contain', filter: 'drop-shadow(0 0 10px rgba(0,255,255,0.2))' }} 
      />
      
      {/* Loading/Error Overlays */}
      {!isLoaded && !error && (
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
          <div className="spinner" style={{ margin: '0 auto 20px' }}></div>
          <p style={{ color: '#00ffff', letterSpacing: '4px' }}>BOOTING VISION...</p>
        </div>
      )}

      {error && (
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(255,0,0,0.1)', display: 'flex', justifyContent: 'center', alignItems: 'center', textAlign: 'center' }}>
          <div style={{ border: '1px solid #ff0055', padding: '40px', background: 'black' }}>
            <h1 style={{ color: '#ff0055' }}>CRITICAL ERROR</h1>
            <p>{error}</p>
            <button onClick={() => window.location.reload()} style={{ background: '#ff0055', color: 'white', border: 'none', padding: '10px 20px', cursor: 'pointer', marginTop: '20px' }}>
              REBOOT SYSTEM
            </button>
          </div>
        </div>
      )}

      {/* HUD Decorations */}
      <div className="hud-overlay">
        <div className="corner top-left" style={{ position: 'absolute', top: 30, left: 30, width: 40, height: 40, borderTop: '1px solid #0ff', borderLeft: '1px solid #0ff' }}></div>
        <div className="corner top-right" style={{ position: 'absolute', top: 30, right: 30, width: 40, height: 40, borderTop: '1px solid #0ff', borderRight: '1px solid #0ff' }}></div>
        <div className="corner bottom-left" style={{ position: 'absolute', bottom: 30, left: 30, width: 40, height: 40, borderBottom: '1px solid #0ff', borderLeft: '1px solid #0ff' }}></div>
        <div className="corner bottom-right" style={{ position: 'absolute', bottom: 30, right: 30, width: 40, height: 40, borderBottom: '1px solid #0ff', borderRight: '1px solid #0ff' }}></div>
        <div className="scanline"></div>
      </div>
    </div>
  );
}

export default App;
