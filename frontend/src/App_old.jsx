import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

import FindResources from './components/FindResources'

function App() {
  const [count, setCount] = useState(0)


  return (
    <>

      <nav className="navbar navbar-expand-lg navbar-light fixed-top navbar-custom">
        <div className="container">
          <a className="navbar-brand d-flex align-items-center" href="#">
            <i className="bi bi-geo-alt-fill me-2 fs-4"></i>
            Natural Resources For Osteoarthritis
          </a>
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav ms-auto">
              <li className="nav-item">
                <a className="nav-link d-flex align-items-center" href="#">
                  <i className="bi bi-house-door me-1"></i>
                  Home
                </a>
              </li>
              <li className="nav-item">
                <a className="nav-link d-flex align-items-center" href="#">
                  <i className="bi bi-info-circle me-1"></i>
                  About
                </a>
              </li>
            </ul>
          </div>
        </div>
      </nav>


      <FindResources />



      {/* Footer */}
      <footer className="footer-custom py-4">
        <div className="container">
          <div className="row">
            <div className="col-12 text-center">
              <p className="mb-2 text-muted">
                <i className="bi bi-c-circle me-1"></i>
                2025 University of Rostock. All rights reserved.
              </p>
              <div className="d-flex justify-content-center gap-3 flex-wrap">
                <a href="#" className="text-muted text-decoration-none">
                  <i className="bi bi-envelope me-1"></i>
                  Contact
                </a>
                <a href="#" className="text-muted text-decoration-none">
                  <i className="bi bi-shield-check me-1"></i>
                  Privacy Policy
                </a>
                <a href="#" className="text-muted text-decoration-none">
                  <i className="bi bi-file-text me-1"></i>
                  Terms of Service
                </a>
              </div>
            </div>
          </div>
        </div>
      </footer>

    </>
  )
}

export default App
