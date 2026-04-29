import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Prime",
    page_icon="flame",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit chrome: header, footer, toolbar, sidebar toggle, and reduce padding
st.markdown(
    """
    <style>
    /* Hide top header bar and toolbar */
    header[data-testid="stHeader"] { display: none !important; }
    div[data-testid="stToolbar"] { display: none !important; }
    div[data-testid="stDecoration"] { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }

    /* Remove page padding so hero fills edge-to-edge */
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    /* Hide sidebar toggle button */
    button[data-testid="collapsedControl"] { display: none !important; }

    /* Make the iframe from components.html fill nicely */
    iframe {
        display: block;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Self-contained HTML blob: WebGL2 shader canvas + overlay content
# ---------------------------------------------------------------------------
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Prime</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }

  html, body {
    width: 100%;
    height: 100%;
    background: #000;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  #c {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    display: block;
  }

  /* ── Overlay ── */
  #overlay {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 24px;
    padding: 40px 24px;
    text-align: center;
    opacity: 0;
    animation: fadeIn 1.2s ease forwards 0.4s;
  }

  @keyframes fadeIn {
    to { opacity: 1; }
  }

  /* Trust badge */
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 20px;
    border-radius: 999px;
    border: 1px solid rgba(251,146,60,0.45);
    background: rgba(251,146,60,0.12);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    color: #fdba74;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.02em;
    transform: translateY(20px);
    animation: slideUp 0.8s cubic-bezier(0.22,1,0.36,1) forwards 0.6s;
    opacity: 0;
  }

  /* Headline */
  .headline {
    transform: translateY(30px);
    animation: slideUp 0.9s cubic-bezier(0.22,1,0.36,1) forwards 0.75s;
    opacity: 0;
    line-height: 1.1;
  }

  .headline-line1 {
    display: block;
    font-size: clamp(52px, 8vw, 96px);
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #fdba74 0%, #fbbf24 45%, #fcd34d 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .headline-line2 {
    display: block;
    font-size: clamp(40px, 6vw, 76px);
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #f97316 0%, #fb923c 50%, #fdba74 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  /* Subtitle */
  .subtitle {
    max-width: 560px;
    font-size: clamp(15px, 2vw, 18px);
    font-weight: 400;
    line-height: 1.65;
    color: rgba(253,186,116,0.75);
    transform: translateY(30px);
    animation: slideUp 0.9s cubic-bezier(0.22,1,0.36,1) forwards 0.9s;
    opacity: 0;
  }

  /* CTA row */
  .cta-row {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    justify-content: center;
    transform: translateY(30px);
    animation: slideUp 0.9s cubic-bezier(0.22,1,0.36,1) forwards 1.05s;
    opacity: 0;
  }

  .btn {
    padding: 14px 32px;
    border-radius: 999px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    border: none;
    outline: none;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
    letter-spacing: 0.01em;
  }

  .btn:hover {
    transform: translateY(-2px);
  }

  .btn-primary {
    background: linear-gradient(135deg, #f97316 0%, #fbbf24 100%);
    color: #1a0a00;
    box-shadow: 0 0 24px rgba(251,146,60,0.5);
  }

  .btn-primary:hover {
    filter: brightness(1.1);
    box-shadow: 0 0 36px rgba(251,146,60,0.7);
  }

  .btn-secondary {
    background: transparent;
    color: #fdba74;
    border: 1.5px solid rgba(251,146,60,0.6);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
  }

  .btn-secondary:hover {
    background: rgba(251,146,60,0.1);
    border-color: #fdba74;
  }

  /* Scroll hint */
  .scroll-hint {
    position: absolute;
    bottom: 28px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    color: rgba(253,186,116,0.4);
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    animation: fadeIn 1s ease forwards 2s;
    opacity: 0;
  }

  .scroll-hint svg {
    animation: bounce 1.8s ease infinite;
  }

  @keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50%       { transform: translateY(6px); }
  }

  @keyframes slideUp {
    to { opacity: 1; transform: translateY(0); }
  }
</style>
</head>
<body>

<canvas id="c"></canvas>

<div id="overlay">
  <div class="badge">
    <span>&#10024;</span>
    <span>Your personal productivity command center</span>
  </div>

  <div class="headline">
    <span class="headline-line1">Prime Dashboard</span>
    <span class="headline-line2">Built in Silence</span>
  </div>

  <p class="subtitle">
    Track your goals, plan your week, fuel your body, and sharpen your mind
    &mdash; all in one place.
  </p>

  <div class="cta-row">
    <a class="btn btn-primary" href="/dashboard" target="_top">
      Open Dashboard &#8594;
    </a>
    <a class="btn btn-secondary" href="/goals" target="_top">
      View Goals
    </a>
  </div>
</div>

<div class="scroll-hint">
  <span>scroll</span>
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M8 3v10M4 9l4 4 4-4" stroke="currentColor" stroke-width="1.5"
          stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</div>

<script>
(function() {
  const canvas = document.getElementById('c');
  const gl = canvas.getContext('webgl2');

  if (!gl) {
    // Fallback: just show a dark gradient background
    canvas.style.background =
      'radial-gradient(ellipse at 60% 40%, #3d1a00 0%, #1a0800 40%, #000 100%)';
    return;
  }

  // ── Vertex shader (full-screen triangle trick) ──
  const VS = `#version 300 es
  out vec2 vUV;
  void main() {
    // 3 hardcoded vertices for a full-screen triangle
    vec2 pos[3];
    pos[0] = vec2(-1.0, -1.0);
    pos[1] = vec2( 3.0, -1.0);
    pos[2] = vec2(-1.0,  3.0);
    gl_Position = vec4(pos[gl_VertexID], 0.0, 1.0);
  }`;

  // ── Fragment shader (GLSL provided in spec) ──
  const FS = `#version 300 es
precision highp float;
out vec4 O;
uniform vec2 resolution;
uniform float time;
#define FC gl_FragCoord.xy
#define T time
#define R resolution
#define MN min(R.x,R.y)
float rnd(vec2 p) {
  p=fract(p*vec2(12.9898,78.233));
  p+=dot(p,p+34.56);
  return fract(p.x*p.y);
}
float noise(in vec2 p) {
  vec2 i=floor(p), f=fract(p), u=f*f*(3.-2.*f);
  float a=rnd(i), b=rnd(i+vec2(1,0)), c=rnd(i+vec2(0,1)), d=rnd(i+1.);
  return mix(mix(a,b,u.x),mix(c,d,u.x),u.y);
}
float fbm(vec2 p) {
  float t=.0, a=1.; mat2 m=mat2(1.,-.5,.2,1.2);
  for (int i=0; i<5; i++) { t+=a*noise(p); p*=2.*m; a*=.5; }
  return t;
}
float clouds(vec2 p) {
  float d=1., t=.0;
  for (float i=.0; i<3.; i++) {
    float a=d*fbm(i*10.+p.x*.2+.2*(1.+i)*p.y+d+i*i+p);
    t=mix(t,d,a); d=a; p*=2./(i+1.);
  }
  return t;
}
void main(void) {
  vec2 uv=(FC-.5*R)/MN,st=uv*vec2(2,1);
  vec3 col=vec3(0);
  float bg=clouds(vec2(st.x+T*.5,-st.y));
  uv*=1.-.3*(sin(T*.2)*.5+.5);
  for (float i=1.; i<12.; i++) {
    uv+=.1*cos(i*vec2(.1+.01*i, .8)+i*i+T*.5+.1*uv.x);
    vec2 p=uv;
    float d=length(p);
    col+=.00125/d*(cos(sin(i)*vec3(1,2,3))+1.);
    float b=noise(i+p+bg*1.731);
    col+=.002*b/length(max(p,vec2(b*p.x*.02,p.y)));
    col=mix(col,vec3(bg*.25,bg*.137,bg*.05),d);
  }
  O=vec4(col,1);
}`;

  function compileShader(type, src) {
    const s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      console.error('Shader compile error:', gl.getShaderInfoLog(s));
      gl.deleteShader(s);
      return null;
    }
    return s;
  }

  const vs = compileShader(gl.VERTEX_SHADER, VS);
  const fs = compileShader(gl.FRAGMENT_SHADER, FS);
  if (!vs || !fs) return;

  const prog = gl.createProgram();
  gl.attachShader(prog, vs);
  gl.attachShader(prog, fs);
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
    console.error('Program link error:', gl.getProgramInfoLog(prog));
    return;
  }

  gl.useProgram(prog);

  const uResolution = gl.getUniformLocation(prog, 'resolution');
  const uTime       = gl.getUniformLocation(prog, 'time');

  // Create an empty VAO for the full-screen triangle (no vertex data needed)
  const vao = gl.createVertexArray();
  gl.bindVertexArray(vao);

  let startTime = performance.now();

  function resize() {
    const dpr = window.devicePixelRatio || 1;
    const w = window.innerWidth;
    const h = window.innerHeight;
    canvas.width  = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    canvas.style.width  = w + 'px';
    canvas.style.height = h + 'px';
    gl.viewport(0, 0, canvas.width, canvas.height);
  }

  window.addEventListener('resize', resize);
  resize();

  function frame() {
    const t = (performance.now() - startTime) * 0.001;
    gl.useProgram(prog);
    gl.uniform2f(uResolution, canvas.width, canvas.height);
    gl.uniform1f(uTime, t);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    requestAnimationFrame(frame);
  }

  requestAnimationFrame(frame);
})();
</script>
</body>
</html>"""

components.html(HTML, height=700, scrolling=False)
