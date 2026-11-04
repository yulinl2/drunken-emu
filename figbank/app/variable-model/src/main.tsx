import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// The web fonts are linked at run time rather than in index.html: the bundler inlines every <link> it finds and
// cannot inline a remote stylesheet. Offline, the system fallbacks in index.css apply.
const fonts = document.createElement('link'); fonts.rel = 'stylesheet'
fonts.href = 'https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap'
document.head.appendChild(fonts)

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
