import React from "react";
import { Link } from "react-router-dom";
import PropTypes from "prop-types";
import '../../assets/css/front.css';
import 'bootstrap/dist/css/bootstrap.min.css'
import "bootstrap-icons/font/bootstrap-icons.css";
//================================|| FRONT LAYOUT ||================================//
const FrontLayout = ({ children }) => {
    return (
        <>
            {/* Navbar */}
            <nav className="navbar navbar-expand-lg navbar-light fixed-top navbar-custom">
                <div className="container">
                    <Link className="navbar-brand d-flex align-items-center" to="/">
                        <i className="bi bi-geo-alt-fill me-2 fs-4"></i>
                        Natural Resources For Osteoarthritis
                    </Link>
                    <button
                        className="navbar-toggler"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#navbarNav"
                    >
                        <span className="navbar-toggler-icon"></span>
                    </button>
                    <div className="collapse navbar-collapse" id="navbarNav">
                        <ul className="navbar-nav ms-auto">
                            <li className="nav-item">
                                <Link className="nav-link d-flex align-items-center" to="/">
                                    <i className="bi bi-house-door me-1"></i>
                                    Home
                                </Link>
                            </li>
                            <li className="nav-item">
                                <Link className="nav-link d-flex align-items-center" to="/about">
                                    <i className="bi bi-info-circle me-1"></i>
                                    About
                                </Link>
                            </li>
                            <li className="nav-item">
                                <Link className="nav-link d-flex align-items-center" to="/login" target="_blank">
                                    <i className="bi bi-person"></i>
                                    Login
                                </Link>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <div className="main-content" style={{ marginTop: "80px" }}>
                {children}
            </div>

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
                                <Link to="/contact" className="text-muted text-decoration-none">
                                    <i className="bi bi-envelope me-1"></i>
                                    Contact
                                </Link>
                                <Link to="/privacy" className="text-muted text-decoration-none">
                                    <i className="bi bi-shield-check me-1"></i>
                                    Privacy Policy
                                </Link>
                                <Link to="/terms" className="text-muted text-decoration-none">
                                    <i className="bi bi-file-text me-1"></i>
                                    Terms of Service
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </footer>
        </>
    );
};

FrontLayout.propTypes = {
    children: PropTypes.node.isRequired
};

export default FrontLayout;
