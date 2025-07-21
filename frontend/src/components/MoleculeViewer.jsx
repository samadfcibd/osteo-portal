import React, { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';

const MoleculeViewer = () => {
    const { fileName } = useParams();
    const viewerRef = useRef(null);
    const containerRef = useRef(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [debugInfo, setDebugInfo] = useState('');

    useEffect(() => {
        const filePath = window.location.origin + '/mol-structure/' + fileName;
        console.log('Original pdbFilePath:', filePath);

        const load3DmolScript = () => {
            return new Promise((resolve, reject) => {
                if (window.$3Dmol) {
                    resolve();
                    return;
                }

                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/3Dmol/2.0.4/3Dmol-min.js';
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            });
        };

        const initializeViewer = async () => {
            try {
                setDebugInfo('Loading 3Dmol.js...');
                await load3DmolScript();

                if (containerRef.current && window.$3Dmol) {
                    setDebugInfo('Creating viewer...');

                    // Create viewer
                    const viewer = window.$3Dmol.createViewer(containerRef.current, {
                        defaultcolors: window.$3Dmol.rasmolElementColors
                    });

                    viewerRef.current = viewer;

                    // Clean up the path
                    let cleanPath = filePath;

                    // Remove /public/ prefix for Vite
                    if (cleanPath.startsWith('/public/')) {
                        cleanPath = cleanPath.replace('/public/', '/');
                    }

                    // Handle double .pdb extension
                    if (cleanPath.endsWith('.pdb.pdb')) {
                        cleanPath = cleanPath.replace('.pdb.pdb', '.pdb');
                    }

                    setDebugInfo(`Fetching PDB file from: ${cleanPath}`);
                    console.log('Cleaned path:', cleanPath);

                    // Load PDB file
                    const response = await fetch(cleanPath);

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    const pdbData = await response.text();
                    setDebugInfo(`PDB file loaded. Size: ${pdbData.length} characters`);

                    console.log('PDB data length:', pdbData.length);
                    console.log('PDB data preview:', pdbData.substring(0, 300));

                    // Validate PDB data
                    if (!pdbData || pdbData.length < 10) {
                        throw new Error('PDB file appears to be empty or too small');
                    }

                    // Check if it's a valid PDB file
                    const hasAtoms = pdbData.includes('ATOM') || pdbData.includes('HETATM');
                    const hasConnect = pdbData.includes('CONECT');
                    const hasHeader = pdbData.includes('HEADER') || pdbData.includes('TITLE');

                    if (!hasAtoms && !hasConnect) {
                        throw new Error('File does not contain ATOM or HETATM records. Please check if this is a valid PDB file.');
                    }

                    setDebugInfo('Adding model to viewer...');

                    // Clear any existing models
                    viewer.removeAllModels();

                    // Add model to viewer with error handling
                    try {
                        viewer.addModel(pdbData, 'pdb');
                        setDebugInfo('Model added successfully. Setting styles...');
                    } catch (modelError) {
                        console.error('Error adding model:', modelError);
                        throw new Error(`Failed to parse PDB data: ${modelError.message}`);
                    }

                    // Set style - cartoon for proteins, stick for small molecules  
                    viewer.setStyle({}, {
                        cartoon: { color: 'spectrum' },
                        stick: { radius: 0.3 }
                    });

                    setDebugInfo('Rendering viewer...');

                    // Center and zoom
                    viewer.zoomTo();
                    viewer.render();

                    setLoading(false);
                    setDebugInfo('3D structure loaded successfully!');
                }
            } catch (err) {
                console.error('Error loading 3D structure:', err);
                setError(`${err.message}\n\nDebug info: ${debugInfo}`);
                setLoading(false);
            }
        };

        initializeViewer();

        // Cleanup
        return () => {
            if (viewerRef.current) {
                try {
                    viewerRef.current.clear();
                } catch (e) {
                    console.log('Cleanup error (non-critical):', e);
                }
            }
        };
    }, [fileName, debugInfo]);

    const handleStyleChange = (style) => {
        if (viewerRef.current) {
            try {
                viewerRef.current.setStyle({}, {});

                switch (style) {
                    case 'cartoon':
                        viewerRef.current.setStyle({}, { cartoon: { color: 'spectrum' } });
                        break;
                    case 'stick':
                        viewerRef.current.setStyle({}, { stick: { radius: 0.3 } });
                        break;
                    case 'sphere':
                        viewerRef.current.setStyle({}, { sphere: { scale: 0.3 } });
                        break;
                    case 'line':
                        viewerRef.current.setStyle({}, { line: {} });
                        break;
                    default:
                        viewerRef.current.setStyle({}, {
                            cartoon: { color: 'spectrum' },
                            stick: { radius: 0.3 }
                        });
                }

                viewerRef.current.render();
            } catch (styleError) {
                console.error('Error changing style:', styleError);
            }
        }
    };

    return (
        <div className="container">
            <div className="row">
                <div className="col-12">
                    <div className="card card-custom mb-4">
                        <div className="card-header d-flex justify-content-between align-items-center">
                            <h5 className="card-title mb-0">3D Structure</h5>
                            {!loading && !error && (
                                <div className="btn-group btn-group-sm" role="group">
                                    {/* <button
                            className="btn btn-outline-primary"
                            onClick={() => handleStyleChange('cartoon')}
                            title="Cartoon View"
                        >
                            Cartoon
                        </button> */}
                                    <button
                                        className="btn btn-outline-primary"
                                        onClick={() => handleStyleChange('stick')}
                                        title="Stick View"
                                    >
                                        Stick
                                    </button>
                                    <button
                                        className="btn btn-outline-primary"
                                        onClick={() => handleStyleChange('sphere')}
                                        title="Sphere View"
                                    >
                                        Sphere
                                    </button>
                                    <button
                                        className="btn btn-outline-primary"
                                        onClick={() => handleStyleChange('line')}
                                        title="Line View"
                                    >
                                        Line
                                    </button>
                                </div>
                            )}
                        </div>

                        <div className="card-body p-0 position-relative" style={{ height: '600px' }}>
                            {loading && (
                                <div className="position-absolute top-50 start-50 translate-middle text-center">
                                    <div className="spinner-border text-primary" role="status">
                                        <span className="visually-hidden">Loading...</span>
                                    </div>
                                    <p className="mt-2 text-muted">Loading 3D structure...</p>
                                    {debugInfo && <small className="text-muted d-block">{debugInfo}</small>}
                                </div>
                            )}

                            {error && (
                                <div className="position-absolute top-50 start-50 translate-middle text-center w-75">
                                    <div className="alert alert-danger">
                                        <h6>Error loading 3D structure</h6>
                                        <pre className="small text-start" style={{ whiteSpace: 'pre-wrap' }}>{error}</pre>
                                        <button
                                            className="btn btn-outline-primary btn-sm mt-2"
                                            onClick={() => window.location.reload()}
                                        >
                                            Retry
                                        </button>
                                    </div>
                                </div>
                            )}

                            <div
                                ref={containerRef}
                                className="w-100 h-100"
                                style={{
                                    backgroundColor: '#000',
                                    borderRadius: '0 0 0.375rem 0.375rem'
                                }}
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MoleculeViewer;