// MoleculeViewerPage.jsx
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import MoleculeViewer from '../components/MoleculeViewer';

const MoleculeViewerPage = () => {
    const { fileName } = useParams();
    const [organism, setOrganism] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // const fetchOrganismData = async () => {
        //     try {
        //         // Replace with your actual API endpoint
        //         const response = await fetch(`/api/organisms/${organismId}`);
        //         const data = await response.json();
        //         setOrganism(data);
        //     } catch (error) {
        //         console.error('Error fetching organism:', error);
        //     } finally {
        //         setLoading(false);
        //     }
        // };

        // fetchOrganismData();
        setLoading(false);
    }, [fileName]);

    if (loading) {
        return (
            <div className="container-fluid p-4">
                <div className="text-center">
                    <div className="spinner-border" role="status">
                        <span className="visually-hidden">Loading...</span>
                    </div>
                </div>
            </div>
        );
    }

    // if (!organism) {
    //     return (
    //         <div className="container-fluid p-4">
    //             <div className="alert alert-danger">
    //                 Organism not found
    //             </div>
    //         </div>
    //     );
    // }

    return (
        <div className="container-fluid p-4">
            <div className="row">
                <div className="col-12">
                    <div className="card">
                        <div className="card-header d-flex justify-content-between align-items-center">
                            <h4 className="mb-0">3D Molecular Structure Viewer</h4>
                            <button
                                className="btn btn-outline-secondary"
                                onClick={() => window.close()}
                            >
                                <i className="bi bi-x"></i> Close Window
                            </button>
                        </div>
                        <div className="card-body">
                            {/* <div className="row mb-4">
                                <div className="col-md-8">
                                    <h5>{organism.organism_name}</h5>
                                    <div className="row">
                                        <div className="col-md-6">
                                            <small className="d-block">
                                                <strong>Protein:</strong> {organism.protein_name}
                                            </small>
                                            <small className="d-block">
                                                <strong>Compound:</strong> {organism.compound_name}
                                            </small>
                                            <small className="d-block">
                                                <strong>Kingdom:</strong> {organism.gbifKingdom}
                                            </small>
                                        </div>
                                        <div className="col-md-6">
                                            {organism.vernacularNames?.length > 0 && (
                                                <div>
                                                    <small><strong>Common Names:</strong></small>
                                                    <div className="d-flex flex-wrap gap-1 mt-1">
                                                        {organism.vernacularNames.map((name, index) => (
                                                            <span key={index} className="badge bg-secondary">
                                                                {name}
                                                            </span>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                                <div className="col-md-4">
                                    {organism.gbifImages?.length > 0 && (
                                        <div className="d-flex gap-2">
                                            {organism.gbifImages.slice(0, 3).map((image, idx) => (
                                                <img
                                                    key={idx}
                                                    src={image}
                                                    alt={organism.organism_name}
                                                    className="rounded"
                                                    style={{ width: '60px', height: '60px', objectFit: 'cover' }}
                                                />
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div> */}

                            <MoleculeViewer
    pdbFilePath={`${window.location.origin}/mol-structure/${fileName}.pdb`}
    organismName="Your Organism Name"
    onClose={() => window.close()}
/>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MoleculeViewerPage;