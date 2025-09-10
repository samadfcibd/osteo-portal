import { useEffect, useRef, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import * as $3Dmol from "3dmol/build/3Dmol-min.js";
import FrontLayout from './FrontLayout';

const MoleculeViewer = () => {
    const { fileName } = useParams();
    const containerRef = useRef(null);
    const viewerRef = useRef(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [currentStyle, setCurrentStyle] = useState("stick");

    const [proteinName, compoundName] = fileName
        ? fileName.split('.')[0].split('-')
        : ['', ''];

    const styleOptions = [
        { type: 'stick', label: 'Stick', icon: 'bi bi-grip-vertical' },
        { type: 'sphere', label: 'Sphere', icon: 'bi bi-circle-fill' },
        { type: 'line', label: 'Line', icon: 'bi bi-slash-lg' },
        { type: 'cartoon', label: 'Cartoon', icon: 'bi bi-bezier2' }
    ];

    const handleStyleChange = useCallback((style) => {
        if (!viewerRef.current) return;

        try {
            viewerRef.current.setStyle({}, {});

            const styles = {
                cartoon: { cartoon: { color: 'spectrum' } },
                stick: { stick: { radius: 0.3, color: 'spectrum' } },
                sphere: { sphere: { scale: 0.3, color: 'spectrum' } },
                line: { line: { color: 'spectrum' } }
            };

            viewerRef.current.setStyle({}, styles[style] || styles.stick);
            viewerRef.current.render();
            setCurrentStyle(style);
        } catch (err) {
            console.error('Style change error:', err);
        }
    }, []);

    useEffect(() => {
        if (!fileName) {
            setError("No file name provided");
            setLoading(false);
            return;
        }

        let isMounted = true;
        const controller = new AbortController();

        const loadMolecule = async () => {
            try {
                // Try both possible endpoints
                const endpoints = [
                    `http://localhost:5000/api/pdb_files/${encodeURIComponent(fileName)}`,
                    `http://localhost:5000/uploads/pdb-files/${encodeURIComponent(fileName)}`
                ];
                
                let data, lastError;
                
                // Try each endpoint until one works
                for (const endpoint of endpoints) {
                    try {
                        console.log("Trying endpoint:", endpoint);
                        const res = await fetch(endpoint, { signal: controller.signal });
                        
                        if (res.ok) {
                            data = await res.text();
                            break;
                        }
                        lastError = `Server returned ${res.status} ${res.statusText}`;
                    } catch (err) {
                        lastError = err.message;
                    }
                }
                
                if (!data) {
                    throw new Error(`Failed to load PDB file. ${lastError}`);
                }

                if (!isMounted) return;

                containerRef.current.innerHTML = "";
                const viewer = $3Dmol.createViewer(containerRef.current, {
                    backgroundColor: "white"
                });

                viewerRef.current = viewer;
                viewer.addModel(data, "pdb");
                handleStyleChange('stick');
                viewer.zoomTo();
                viewer.render();

                setLoading(false);
            } catch (err) {
                if (isMounted) {
                    console.error("Error loading molecule:", err);
                    setError(err.message);
                    setLoading(false);
                }
            }
        };

        loadMolecule();

        return () => {
            isMounted = false;
            controller.abort();
            if (viewerRef.current) {
                viewerRef.current.clear();
            }
        };
    }, [fileName, handleStyleChange]);

    return (
        <FrontLayout>
            <div className="container mt-4">
                <div className="row">
                    <div className="col-12">
                        <div className="card card-custom mb-4 border-0 shadow-sm">
                            <div className="card-header bg-white border-0 d-flex justify-content-between align-items-center py-3">
                                <div>
                                    <h5 className="mb-0 fw-semibold">
                                        <i className="bi bi-box-seam me-2 text-primary"></i>
                                        Molecular Viewer
                                    </h5>
                                    <small className="text-muted">
                                        {proteinName && compoundName && (
                                            <>
                                                Protein: <span className="text-dark">{proteinName}</span> |
                                                Compound: <span className="text-dark">{compoundName}</span>
                                            </>
                                        )}
                                    </small>
                                </div>

                                {!loading && !error && (
                                    <div className="btn-group btn-group-sm" role="group">
                                        {styleOptions.map((option) => (
                                            <button
                                                key={option.type}
                                                className={`btn btn-outline-secondary ${currentStyle === option.type ? "active" : ""}`}
                                                onClick={() => handleStyleChange(option.type)}
                                                title={`${option.label} View`}
                                            >
                                                <i className={option.icon}></i>
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>

                            <div className="card-body p-0 position-relative" style={{ height: '600px' }}>
                                {loading && (
                                    <div className="position-absolute top-50 start-50 translate-middle text-center">
                                        <div className="spinner-grow text-primary" role="status">
                                            <span className="visually-hidden">Loading...</span>
                                        </div>
                                        <p className="mt-3 text-muted">Loading molecular structure...</p>
                                    </div>
                                )}

                                {error && (
                                    <div className="position-absolute top-50 start-50 translate-middle text-center w-75">
                                        <div className="alert alert-danger border-0 shadow-sm">
                                            <div className="d-flex align-items-center">
                                                <i className="bi bi-exclamation-triangle-fill me-2"></i>
                                                <h6 className="mb-0">Loading Error</h6>
                                            </div>
                                            <hr />
                                            <p className="small mb-2">{error}</p>
                                            <p className="small text-muted">
                                                Please check that:
                                                <br />- The Flask server is running on port 5000
                                                <br />- The file exists in the uploads directory
                                                <br />- The server has a route to serve PDB files
                                            </p>
                                            <button
                                                className="btn btn-sm btn-outline-primary"
                                                onClick={() => window.location.reload()}
                                            >
                                                <i className="bi bi-arrow-clockwise me-1"></i> Retry
                                            </button>
                                        </div>
                                    </div>
                                )}

                                <div
                                    ref={containerRef}
                                    className="w-100 h-100"
                                    style={{
                                        backgroundColor: '#fff',
                                        borderRadius: '0 0 0.375rem 0.375rem',
                                        minHeight: '400px'
                                    }}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </FrontLayout>
    );
};

export default MoleculeViewer;