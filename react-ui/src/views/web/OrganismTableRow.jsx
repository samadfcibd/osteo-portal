import React, { useState } from 'react';
import StarRating from "./StarRating";

const OrganismTableRow = ({ organism, onRate, onViewReviews }) => {

    return (
        <tr key={organism.data_id}>
            <td>
                <div className="d-flex align-items-center">
                    <div>
                        <h6 className="mb-0">{organism.organism_name}</h6>
                        <small className={organism.gbifFound ? 'text-success' : 'text-danger'}>
                            {organism.gbifFound ? '✅ Found in your country' : '❌ Not Found in your country'}
                        </small>
                    </div>
                </div>
            </td>
            <td style={{ maxWidth: "200px" }}>
                <div className="d-flex flex-wrap gap-1">
                    {organism.vernacularNames?.length > 0 ? (
                        organism.vernacularNames.map((name, index) => (
                            <span key={index} className="badge bg-success text-light" style={{ whiteSpace: "wrap" }}>
                                {name}
                            </span>
                        ))
                    ) : (
                        <span className="badge bg-light text-dark">No common names found</span>
                    )}
                </div>
            </td>
            <td>
                <StarRating rating={organism.rating} />
                <div className="d-flex gap-2 mt-1">
                    <button
                        className="btn btn-sm btn-outline-primary"
                        onClick={() => onRate(organism)}
                    >
                        <i className="bi bi-star me-1"></i>Rate
                    </button>
                    <button
                        className="btn btn-sm btn-outline-secondary"
                        onClick={() => onViewReviews(organism.organism_id)}
                    >
                        <i className="bi bi-chat-square-text me-1"></i>Reviews
                    </button>
                </div>
            </td>
            <td>
                <div className="d-flex">
                    {organism.gbifImages?.slice(0, 2).map((image, idx) => (
                        <img
                            key={idx}
                            src={image}
                            alt={organism.organism_name}
                            className="rounded me-2"
                            style={{ width: '50px', height: '50px', objectFit: 'cover', cursor: 'pointer' }}
                            onClick={() => window.open(image, '_blank')}
                        />
                    ))}
                    {(!organism.gbifImages || organism.gbifImages.length === 0) && (
                        <span className="text-muted">No images found</span>
                    )}
                </div>
            </td>
            {/* <td>
                <small className="d-block mb-1">
                    Organism Type: <i style={{ textTransform: 'capitalize' }}>{organism.gbifKingdom}</i>
                </small>
                <small className="d-block mb-1">
                    Protein:{" "}
                    {[...new Set(organism.compound_protein_model.map(item => item.protein))].map((protein, index, array) => (
                        <React.Fragment key={protein}>
                            <i style={{ textTransform: 'capitalize' }}>
                                {protein}
                            </i>
                            {index < array.length - 1 && ", "}
                        </React.Fragment>
                    ))}
                </small>
                <small className="d-block mb-1">
                    Compound:{" "}
                    {[...new Set(organism.compound_protein_model.map(item => item.compound))].map((compound, index, array) => {
                        // Find the first item with this compound name to get its pubchem_id
                        const compoundItem = organism.compound_protein_model.find(item => item.compound === compound);
                        const pubchemId = compoundItem?.pubchem_id;

                        return (
                            <React.Fragment key={compound}>
                                {pubchemId && pubchemId !== "NULL" ? (
                                    <a
                                        href={`https://pubchem.ncbi.nlm.nih.gov/compound/${pubchemId}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        title='Explore compound details on PubChem'
                                        style={{ textTransform: 'capitalize', textDecoration: 'none' }}
                                    >
                                        {compound}
                                    </a>
                                ) : (
                                    <i style={{ textTransform: 'capitalize' }}>
                                        {compound}
                                    </i>
                                )}
                                {index < array.length - 1 && ", "}
                            </React.Fragment>
                        );
                    })}
                </small>
                <div className="d-flex gap-2 flex-wrap">
                    {organism.compound_protein_model.map((item, index) => (
                        <button
                            key={index}
                            className="btn btn-sm btn-outline-dark"
                            onClick={() => window.open(`/3d-viewer/${item.model}`, '_blank')}
                            title='Protien-Compound Interaction 3D Model'
                        >
                            <span style={{ textTransform: 'capitalize' }}>
                                {item.protein}
                            </span>
                            {" -> "}
                            <span style={{ textTransform: 'capitalize' }}>
                                {item.compound}
                            </span>
                        </button>
                    ))}
                </div>
            </td> */}

            <td>
                <small className="d-block mb-1">
                    Organism Type: <i style={{ textTransform: 'capitalize' }}>{organism.gbifKingdom}</i>
                </small>

                {/* Group by protein and display each protein-compound pair separately */}
                {Object.entries(
                    organism.compound_protein_model.reduce((acc, item) => {
                        if (!acc[item.protein]) {
                            acc[item.protein] = [];
                        }
                        acc[item.protein].push(item);
                        return acc;
                    }, {})
                ).map(([protein, items]) => (
                    <div key={protein} className="p-2 border-top mb-2 bg-light bg-gradient border-secondary">
                        <small className="d-block mb-1">
                            Protein: <i style={{ textTransform: 'capitalize' }}>{protein}</i>
                        </small>
                        <small className="d-block mb-1">
                            Compound:{" "}
                            {items.map((item, index, array) => {
                                const pubchemId = item?.pubchem_id;
                                return (
                                    <React.Fragment key={`${protein}-${item.compound}-${index}`}>
                                        {pubchemId && pubchemId !== "NULL" ? (
                                            <a
                                                href={`https://pubchem.ncbi.nlm.nih.gov/compound/${pubchemId}`}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                title='Explore compound details on PubChem'
                                                style={{ textTransform: 'capitalize', textDecoration: 'none' }}
                                            >
                                                {item.compound}
                                            </a>
                                        ) : (
                                            <i style={{ textTransform: 'capitalize' }}>
                                                {item.compound}
                                            </i>
                                        )}
                                        {index < array.length - 1 && ", "}
                                    </React.Fragment>
                                );
                            })}
                        </small>
                        <div className="d-flex gap-2 flex-wrap">
                            {items.map((item, index) => (
                                <button
                                    key={index}
                                    className="btn btn-sm btn-outline-dark"
                                    onClick={() => window.open(`/3d-viewer/${item.model}`, '_blank')}
                                    title={`${item.protein} - ${item.compound} interaction 3D model`}
                                >
                                    Protein-Compound Interaction
                                </button>
                            ))}
                        </div>
                    </div>
                ))}
            </td>
        </tr >
    );
};

export default OrganismTableRow;